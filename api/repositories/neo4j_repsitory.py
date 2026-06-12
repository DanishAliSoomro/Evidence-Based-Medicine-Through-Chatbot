import re
from neo4j import GraphDatabase
from config import settings
from api.services.graph_extractor import CombinedGraphChunk

class Neo4jRepository:
    # --- Schema Definitions ---
    CONSTRAINTS = [
        "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
        "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE"
    ]

    INDEXES = [
        """
        CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
        FOR (c:Chunk) ON (c.embedding)
        OPTIONS {indexConfig: {
          `vector.dimensions`: 384,
          `vector.similarity_function`: 'cosine'
        }}
        """,
        """
        CREATE FULLTEXT INDEX entity_name_fuzzy IF NOT EXISTS
        FOR (e:Entity) ON EACH [e.name]
        """
    ]

    # --- CRUD Queries ---
    QUERY_MERGE_CHUNK = """
    MERGE (c:Chunk {id: $id})
    SET c.text = $text,
        c.page_number = $page_number,
        c.embedding = $embedding
    """

    QUERY_MERGE_ENTITY = """
    MERGE (e:Entity {name: $name})
    ON CREATE SET e.type = $type, e.description = $description
    ON MATCH SET e.description = CASE 
        WHEN size($description) > size(e.description) THEN $description 
        ELSE e.description END
    """

    QUERY_LINK_CHUNK_TO_ENTITY = """
    MATCH (c:Chunk {id: $chunk_id})
    MATCH (e:Entity {name: $entity_name})
    MERGE (c)-[:MENTIONS]->(e)
    """

    QUERY_MERGE_RELATIONSHIP = """
    MATCH (s:Entity {name: $source})
    MATCH (t:Entity {name: $target})
    MERGE (s)-[r:RELATED_TO]->(t)
    ON CREATE SET r.descriptions = [$description], r.strength = $strength
    ON MATCH SET 
        r.descriptions = CASE 
            WHEN NOT $description IN r.descriptions THEN r.descriptions + $description 
            ELSE r.descriptions END,
        r.strength = CASE WHEN $strength > r.strength THEN $strength ELSE r.strength END
    """

    # --- Retrieval Query ---
    QUERY_HYBRID_RETRIEVAL = """
    CALL db.index.vector.queryNodes('chunk_embeddings', $top_k, $query_embedding)
    YIELD node AS chunk, score
    MATCH (chunk)-[:MENTIONS]->(e:Entity)
    OPTIONAL MATCH (e)-[r:RELATED_TO]-(neighbor:Entity)
    RETURN 
        collect(DISTINCT chunk.text) AS chunk_contexts,
        collect(DISTINCT {
            name: e.name, 
            type: e.type, 
            description: e.description
        }) AS entities,
        collect(DISTINCT {
            source: e.name, 
            target: neighbor.name, 
            description: r.descriptions, 
            strength: r.strength
        }) AS relationships
    """

    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
        self.database = settings.NEO4J_DATABASE

    def close(self):
        self.driver.close()

    def initialize_schema(self):
        """Sets up constraints and indexes required for GraphRAG."""
        with self.driver.session(database=self.database) as session:
            for statement in self.CONSTRAINTS + self.INDEXES:
                session.run(statement)
        print("Neo4j schema (indexes and constraints) initialized with 384 dimensions.")

    def _find_fuzzy_match(self, tx, entity_name: str, threshold=0.8):
        """Uses full-text search to find an existing entity with a similar name."""
        clean_name = re.sub(r'([+\-&|!(){}\[\]^"~*?:\\/])', r'\\\1', entity_name)
        query = f"CALL db.index.fulltext.queryNodes('entity_name_fuzzy', '{clean_name}~0.8') " \
                "YIELD node, score RETURN node.name AS name, score LIMIT 1"
        result = tx.run(query)
        record = result.single()
        if record and record["score"] > threshold:
            return record["name"]
        return None

    def store_combined_results(self, results: list[CombinedGraphChunk]):
        """Main entry point to ingest the results."""
        print(f"Storing {len(results)} chunks and their graph data into Neo4j...")
        for result in results:
            self.ingest_chunk_data(result)

    def ingest_chunk_data(self, data: CombinedGraphChunk):
        with self.driver.session(database=self.database) as session:
            session.execute_write(self._merge_chunk, data.chunk)

            name_map = {}
            for entity in data.entities:
                matched_name = session.execute_read(self._find_fuzzy_match, entity.name)
                final_name = matched_name if matched_name else entity.name
                name_map[entity.name] = final_name

                session.execute_write(self._merge_entity, final_name, entity.type, entity.description)
                session.execute_write(self._create_mentions_rel, data.chunk.chunk_id, final_name)

            for rel in data.relationships:
                source = name_map.get(rel.source, rel.source)
                target = name_map.get(rel.target, rel.target)
                session.execute_write(self._merge_relationship, source, target, rel.description, rel.strength)

    def _merge_chunk(self, tx, chunk):
        tx.run(self.QUERY_MERGE_CHUNK, id=chunk.chunk_id, text=chunk.content,
               page_number=chunk.page_number, embedding=chunk.embedding)

    def _merge_entity(self, tx, name, entity_type, description):
        tx.run(self.QUERY_MERGE_ENTITY, name=name, type=entity_type, description=description)

    def _create_mentions_rel(self, tx, chunk_id, entity_name):
        tx.run(self.QUERY_LINK_CHUNK_TO_ENTITY, chunk_id=chunk_id, entity_name=entity_name)

    def _merge_relationship(self, tx, source, target, description, strength):
        tx.run(self.QUERY_MERGE_RELATIONSHIP, source=source, target=target, description=description, strength=strength)

    def retrieve_hybrid_context(self, query_embedding: list[float], top_k: int = 5):
        """Performs hybrid retrieval: Vector Search + Graph Traversal."""
        with self.driver.session(database=self.database) as session:
            result = session.run(
                self.QUERY_HYBRID_RETRIEVAL,
                query_embedding=query_embedding, 
                top_k=top_k
            )
            record = result.single()
            if not record:
                return {"chunk_contexts": [], "entities": [], "relationships": []}
            return {
                "chunk_contexts": record["chunk_contexts"],
                "entities": record["entities"],
                "relationships": record["relationships"]
            }
