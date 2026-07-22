import json
from api.repositories.neo4j_repsitory import Neo4jRepository
from api.services.text_chunker import TextChunker
from api.services.prompts import GUARDRAIL, PICO_Rules, SYSTEM_PROMPT, RISK_CLASSIFIER, REFORMAT_CHECK, PMC_identifier
from openai import OpenAI
from config import settings

RELEVANCE_THRESHOLD = 0.75


class GraphRAGService:
    def __init__(self):
        self.neo4j_svc = Neo4jRepository()
        self.chunker = TextChunker()
        self.client = OpenAI(
            base_url=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY
        )
        self.conversation_history = []

    def _llm_json(self, system: str, user: str, max_tokens: int = 20) -> dict:
        raw = self.client.chat.completions.create(
            model=settings.AZURE_DEPLOYMENT_NAME,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0,
            max_tokens=max_tokens,
        ).choices[0].message.content.strip()
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def _classify_query(self, query: str) -> str:
        messages = [{"role": "system", "content": GUARDRAIL}]
        # Give the guardrail the last exchange so follow-up questions aren't blocked
        if self.conversation_history:
            messages.extend(self.conversation_history[-2:])
        messages.append({"role": "user", "content": query})
        raw = self.client.chat.completions.create(
            model=settings.AZURE_DEPLOYMENT_NAME,
            messages=messages,
            temperature=0,
            max_tokens=20,
        ).choices[0].message.content.strip()
        try:
            return json.loads(raw).get("class", "medical")
        except Exception:
            return "medical"

    def _check_reformat(self, query: str) -> str:
        return self._llm_json(REFORMAT_CHECK, query).get("type", "new_question")

    def _classify_risk(self, query: str) -> str:
        return self._llm_json(RISK_CLASSIFIER, query).get("risk", "informational")

    def _run_pico(self, query: str) -> str:
        raw = self.client.chat.completions.create(
            model=settings.AZURE_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": PICO_Rules},
                {"role": "user",   "content": query},
            ],
            temperature=0,
            max_tokens=300,
        ).choices[0].message.content.strip()

        if "Status: VALID" not in raw:
            return query

        lines = {l.split(":")[0].strip(): l.split(":", 1)[1].strip()
                 for l in raw.splitlines() if ":" in l and l.split(":")[0].strip() in ("P", "I", "C", "O")}

        def _val(key):
            v = lines.get(key, "")
            return v if v and "<MISSING>" not in v else ""

        parts = [f"In {_val('P')}" if _val("P") else "",
                 f"does {_val('I')}" if _val("I") else "",
                 f"compared to {_val('C')}" if _val("C") else "",
                 f"improve {_val('O')}" if _val("O") else ""]
        structured = " ".join(p for p in parts if p) + "?"
        print(f"[PICO] VALID → {structured}")
        return structured

    def perform_graph_rag(self, user_query: str, pdf_context: str = None) -> str:
        # Step 0 — Reformat check (skip full pipeline if user just wants a reformat)
        last_assistant = next(
            (m["content"] for m in reversed(self.conversation_history) if m["role"] == "assistant"),
            None,
        )
        if last_assistant:
            reformat_type = self._check_reformat(user_query)
            print(f"[Reformat] {reformat_type}")
            if reformat_type == "reformat":
                completion = self.client.chat.completions.create(
                    model=settings.AZURE_DEPLOYMENT_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "assistant", "content": last_assistant},
                        {"role": "user", "content": user_query},
                    ],
                    temperature=0,
                )
                answer = completion.choices[0].message.content
                self.conversation_history.append({"role": "user", "content": user_query})
                self.conversation_history.append({"role": "assistant", "content": answer})
                return answer

        # Step 0b — Source query detection: "which PMC article / source / reference is this from?"
        _source_keywords = ("pmc", "source", "reference", "article", "citation", "where did", "which paper", "which study", "published")
        if last_assistant and any(k in user_query.lower() for k in _source_keywords):
            print("[Source Query] Detected — using PMC_identifier on conversation context")
            completion = self.client.chat.completions.create(
                model=settings.AZURE_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": PMC_identifier},
                    {"role": "user", "content": f"The following is the answer I gave the user:\n\n{last_assistant}\n\nUser is now asking: {user_query}"},
                ],
                temperature=0,
                max_tokens=200,
            )
            answer = completion.choices[0].message.content
            self.conversation_history.append({"role": "user", "content": user_query})
            self.conversation_history.append({"role": "assistant", "content": answer})
            return answer

        # Step 1 — Guardrail (skip if a PDF is loaded — it was already verified as medical on upload)
        if pdf_context:
            query_class = "medical"
        else:
            query_class = self._classify_query(user_query)
        print(f"[Guardrail] {query_class}")
        if query_class == "off_topic":
            return "I can only assist with medical and clinical questions. Please ask something related to healthcare or medicine."

        # Step 2 — PICO enhancement for better retrieval
        retrieval_query = self._run_pico(user_query)

        # Step 3 — Vector search
        print("\n[Step 1] Embedding query and performing vector search...")
        query_embedding = self.chunker.compute_embeddings([retrieval_query])[0]

        # Step 4 — Graph traversal
        print("[Step 2] Traversing graph for related entities and facts...")
        context_data = self.neo4j_svc.retrieve_hybrid_context(query_embedding, top_k=5)

        # Step 5 — Relevance filtering (score >= 0.75)
        print("[Step 3] Filtering by relevance threshold...")
        filtered = [c for c in context_data["chunk_contexts"] if c.get("score", 0) >= RELEVANCE_THRESHOLD]
        chunk_texts = [c["text"] for c in filtered]

        direct_context  = "\n".join([f"- {t}" for t in chunk_texts])
        entity_context  = "\n".join([
            f"- {e['name']} ({e['type']}): {e['description']}"
            for e in context_data["entities"] if e.get("name")
        ])
        graph_context   = "\n".join([
            f"- {r['source']} is related to {r['target']} because: {', '.join(r['description']) if isinstance(r['description'], list) else r['description']}"
            for r in context_data["relationships"] if r.get("target")
        ])

        # Step 6 — If no relevant context, apply risk classifier
        if not chunk_texts and not pdf_context:
            risk = self._classify_risk(user_query)
            print(f"[Risk] No context — {risk}")
            if risk == "actionable":
                return (
                    "I don't have specific evidence in my knowledge base for this question, and it involves "
                    "a clinical decision that requires verified medical evidence. Please consult a qualified "
                    "healthcare professional or refer to authoritative clinical guidelines."
                )
            completion = self.client.chat.completions.create(
                model=settings.AZURE_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *self.conversation_history,
                    {"role": "user", "content": (
                        f"{user_query}\n\n"
                        "(Note: No matching documents found in the knowledge base. "
                        "Answer using general medical knowledge and clearly state this.)"
                    )},
                ],
                temperature=0,
            )
            answer = completion.choices[0].message.content
            self.conversation_history.append({"role": "user", "content": user_query})
            self.conversation_history.append({"role": "assistant", "content": answer})
            return answer

        # Step 7 — Generate answer from retrieved context
        print("[Step 4] Generating final answer from LLM...")

        if pdf_context:
            full_prompt = f"""
A PDF document has been uploaded by the user. Answer the question using the PDF as your PRIMARY source.

STRICT RULES when a PDF is loaded:
- Answer from the PDF content first and foremost.
- Only use the knowledge base sections below if the PDF does not cover the question.
- Do NOT blend information from previous conversation topics that are unrelated to this PDF.
- If the answer is clearly in the PDF, do not contradict it or supplement it with unrelated graph data.

### UPLOADED PDF (PRIMARY SOURCE)
{pdf_context[:8000]}

### KNOWLEDGE BASE CHUNKS (use only if PDF does not answer the question)
{direct_context if direct_context else "No matching chunks found."}

### KEY ENTITIES
{entity_context if entity_context else "None found."}

### KNOWLEDGE GRAPH RELATIONSHIPS
{graph_context if graph_context else "None found."}

USER QUESTION: {user_query}
"""
        else:
            full_prompt = f"""
Answer the user question based on the provided context and our previous conversation.

### KNOWLEDGE BASE CHUNKS (VECTOR SEARCH)
{direct_context if direct_context else "No matching chunks found in knowledge base."}

### KEY ENTITIES
{entity_context if entity_context else "No key entities found."}

### KNOWLEDGE GRAPH RELATIONSHIPS
{graph_context if graph_context else "No relational facts found."}

USER QUESTION: {user_query}
(Note: retrieval was performed using an enhanced structured query for better context accuracy)
"""

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": full_prompt})

        completion = self.client.chat.completions.create(
            model=settings.AZURE_DEPLOYMENT_NAME,
            messages=messages,
            temperature=0,
        )
        answer = completion.choices[0].message.content

        self.conversation_history.append({"role": "user", "content": user_query})
        self.conversation_history.append({"role": "assistant", "content": answer})
        return answer

    def reset_conversation(self):
        self.conversation_history = []

    def close(self):
        self.neo4j_svc.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    print("\n" + "=" * 50)
    print("      MEDICAL GRAPHRAG INTERACTIVE CHAT")
    print("=" * 50)
    print("Type 'exit' or 'quit' to end the session.\n")

    with GraphRAGService() as service:
        while True:
            user_input = input("\nUser: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Ending session. Goodbye!")
                break
            try:
                answer = service.perform_graph_rag(user_input)
                print("\n--- Assistant ---")
                print(answer)
                print("-" * 30)
            except Exception as e:
                print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()
