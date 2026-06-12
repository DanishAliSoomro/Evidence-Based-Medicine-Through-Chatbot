import os
from api.services.pdf_extractor import PDFExtractor
from api.services.text_chunker import TextChunker
from api.services.graph_extractor import GraphRelationExtractor
from api.repositories.neo4j_repsitory import Neo4jRepository


class PDFProcessingService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100, iter_size: int = 4):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.iter_size = iter_size
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.graph = GraphRelationExtractor()

    def process_pdf_file(self, pdf_path: str, source_id: str | None = None) -> list:
        """
        Processes a single PDF file: extracts text, chunks it, generates embeddings,
        extracts entity relationships, and stores the results in Neo4j.
        """
        print(f"\n" + "=" * 60)
        print(f"Processing File: {os.path.basename(pdf_path)}")
        print("=" * 60)

        # 1. Extraction
        print(f"Extracting text from {pdf_path}...")
        extractor = PDFExtractor(pdf_path)
        extracted_pages = extractor.extract_text()

        # 2. Chunking + embedding
        print("Chunking extracted text and generating embeddings...")
        all_chunks = self.chunker.process_extracted_data(
            [p.dict() for p in extracted_pages],
            source_id=source_id or os.path.splitext(os.path.basename(pdf_path))[0],
        )
        print(f"Total pages extracted: {len(extracted_pages)}")
        print(f"Total chunks created: {len(all_chunks)}")

        if not all_chunks:
            print(f"No chunks to process for graph extraction in {pdf_path}.")
            return []

        # 3. Relationship extraction per chunk + Neo4j storage
        start = 0
        chunk_len = len(all_chunks)
        all_combined_results = []

        print("\nInitializing Neo4j storage...")
        neo4j_svc = Neo4jRepository()
        neo4j_svc.initialize_schema()

        try:
            while start < chunk_len:
                end_idx = min(start + self.iter_size, chunk_len)
                print(f"\nRunning per-chunk entity-relationship extraction for chunks {start} to {end_idx}...")
                result = self.graph.extract_for_chunks(all_chunks[start:end_idx])

                if result:
                    all_combined_results.extend(result)
                    sample = result[0]
                    print(f"Processing chunk {sample.chunk.chunk_id} and storing information...")
                    print(f"Entities: {len(sample.entities)} | Relationships: {len(sample.relationships)}")
                    print(f"Preview: {sample.chunk.content[:150]}...")

                # 4. Store in Neo4j
                try:
                    neo4j_svc.store_combined_results(result)
                    print(f"Batch {start}-{end_idx} successfully stored in Neo4j.")
                except Exception as e:
                    print(f"Error storing batch in Neo4j: {e}")

                start += self.iter_size

            print(f"\nCompleted processing: {os.path.basename(pdf_path)}")
            print(f"Total combined results extracted: {len(all_combined_results)}")

        finally:
            neo4j_svc.close()

        return all_combined_results

    def process_directory(self, dataset_dir: str) -> dict:
        """
        Processes all PDF files found in the given directory.
        Returns a summary dict with results per file.
        """
        if not os.path.exists(dataset_dir):
            print(f"Error: Directory not found: {dataset_dir}")
            return {}

        pdf_files = [
            os.path.join(dataset_dir, f)
            for f in os.listdir(dataset_dir)
            if f.lower().endswith(".pdf")
        ]

        if not pdf_files:
            print(f"No PDF files found in {dataset_dir}")
            return {}

        print(f"Found {len(pdf_files)} PDF files. Starting batch processing...")

        summary = {}
        for pdf_path in pdf_files:
            try:
                results = self.process_pdf_file(pdf_path)
                summary[pdf_path] = {"status": "success", "total_results": len(results)}
            except Exception as e:
                print(f"CRITICAL ERROR processing {pdf_path}: {e}")
                summary[pdf_path] = {"status": "failed", "error": str(e)}

        return summary


def main():
    dataset_dir = r"C:\Users\HP\Documents\Training Proj\EBM testing\PMC-articles"

    service = PDFProcessingService(chunk_size=1000, chunk_overlap=100, iter_size=4)
    service.process_directory(dataset_dir)


if __name__ == "__main__":
    main()
