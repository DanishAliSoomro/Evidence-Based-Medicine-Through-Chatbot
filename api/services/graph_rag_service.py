from api.repositories.neo4j_repsitory import Neo4jRepository
from api.services.text_chunker import TextChunker
from openai import OpenAI
from config import settings


class GraphRAGService:
    def __init__(self):
        self.neo4j_svc = Neo4jRepository()
        self.chunker = TextChunker()
        self.client = OpenAI(
            base_url=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY
        )
        self.conversation_history = []

    def perform_graph_rag(self, user_query: str) -> str:
        """
        Step-by-step GraphRAG execution with conversation history:
        1. Vector Search Entry Point
        2. Graph Traversal Expansion
        3. Context Augmentation Fusion
        4. LLM Generation with history
        """

        # TODO: every step can also be implemented as SSE for showing progress in the frontend. For now, we keep it simple.

        # 1. Vector Search Entry Point
        print("\n[Step 1] Embedding query and performing vector search...")
        query_embedding = self.chunker.compute_embeddings([user_query])[0]

        # 2. Graph Traversal Expansion
        print("[Step 2] Traversing graph for related entities and facts...")
        context_data = self.neo4j_svc.retrieve_hybrid_context(query_embedding, top_k=5)

        # 3. Context Augmentation Fusion
        print("[Step 3] Fusing vector and graph context...")

        direct_context = "\n".join([f"- {c}" for c in context_data['chunk_contexts']])

        entity_context = "\n".join([
            f"- {e['name']} ({e['type']}): {e['description']}"
            for e in context_data['entities']
        ])

        graph_context = "\n".join([
            f"- {r['source']} is related to {r['target']} because: {', '.join(r['description']) if isinstance(r['description'], list) else r['description']}"
            for r in context_data['relationships'] if r['target']
        ])

        full_prompt = f"""
            Answer the user question based strictly on the provided context sections and our previous conversation.

            ### SECTION 1: DIRECT TEXT CONTEXT (FROM PDF CHUNKS)
            {direct_context if direct_context else "No direct text context found."}

            ### SECTION 2: KEY ENTITIES (KNOWLEDGE BASE)
            {entity_context if entity_context else "No key entities found."}

            ### SECTION 3: KNOWLEDGE GRAPH RELATIONSHIPS (RELATIONAL FACTS)
            {graph_context if graph_context else "No relational facts found."}

            USER QUESTION: {user_query}

            Moreover, Please note the following guidelines for answering:
            You are a smart content formatter and explainer.

            Your goal is to produce the most readable and well-structured answer based on the content, not to force a single format.

            Follow these rules:

            1. Decide the best format dynamically:

            * Use a numbered list when presenting multiple distinct items or options
            * Use paragraphs when explaining a concept in depth
            * Use a mix of short paragraphs + lists when appropriate
            * Avoid forcing everything into lists

            2. When using lists:

            * Add a blank line between each item
            * Keep each item concise (1–2 lines)

            3. Highlight key concepts:

            * Bold the most important keywords or phrases using Markdown (**keyword**)
            * Focus on meaningful, domain-specific terms (not generic words)
            * Do not overuse bold — only highlight what helps scanning

            4. Maintain clean Markdown:

            * No trailing spaces for line breaks
            * Ensure compatibility with GitHub Flavored Markdown (GFM)

            5. Structure for readability:

            * Break content into logical sections if needed
            * Avoid large dense blocks of text
            * Keep the flow natural and human-like

            6. Do NOT add meta commentary about formatting choices.

            Your response should feel natural, well-organized, and easy to scan — not mechanical.

            Now generate the best possible answer accordingly.



        """

        # 4. LLM Generation
        print("[Step 4] Generating final answer from LLM...")

        messages = [
            {"role": "system", "content": "You are a professional medical assistant using a GraphRAG system."}
        ]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": full_prompt})

        completion = self.client.chat.completions.create(
            model=settings.AZURE_DEPLOYMENT_NAME,
            messages=messages,
            temperature=0
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

            if user_input.lower() in ['exit', 'quit']:
                print("Ending session. Goodbye!")
                break

            try:
                answer = service.perform_graph_rag(user_input)
                print("\n--- Assistant ---")
                print(answer)
                print("-" * 30)

            except Exception as e:
                print(f"\nAn error occurred during query processing: {e}")


if __name__ == "__main__":
    main()