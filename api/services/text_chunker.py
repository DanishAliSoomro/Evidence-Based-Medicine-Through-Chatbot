from functools import lru_cache
import re

from sentence_transformers import SentenceTransformer
from api.schemas import Chunk

@lru_cache(maxsize=1)
def get_sentence_transformer_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

class TextChunker:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ):
        """
        Initializes the TextChunker.
        :param chunk_size: Number of characters in each chunk.
        :param chunk_overlap: Number of characters to overlap between chunks.
        :param cache_path: Optional path to save/load chunk embeddings.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Using a small, efficient model for embeddings (384 dimensions)
        # This model is pre-trained and ALWAYS returns a 384-dimension vector.
        self.model = get_sentence_transformer_model()

    def chunk_text(self, text: str) -> list[str]:
        """
        Splits a single string into chunks.
        """
        if not text:
            return []

        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())

            start += (self.chunk_size - self.chunk_overlap)
            if start >= len(text) - self.chunk_overlap and start < len(text):
                remaining = text[start:]
                if remaining.strip():
                    chunks.append(remaining.strip())
                break

        return [c for c in chunks if c]

    def compute_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Compute embeddings using SentenceTransformer.
        These are ALWAYS 384-dimensional.
        """
        if not texts:
            return []
        
        # This will return a list of 384-length vectors
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def _build_chunk_id(self, source_id: str | None, page_num: int, chunk_index: int) -> str:
        if not source_id:
            return f"p{page_num}-c{chunk_index}"

        safe_source_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", source_id).strip("-")
        return f"{safe_source_id}-p{page_num}-c{chunk_index}"

    def process_extracted_data(self, extracted_data: list[dict], source_id: str | None = None) -> list[Chunk]:
        """
        Takes PDF extraction output and returns Chunk objects with embeddings.
        """
        all_chunks = []
        for item in extracted_data:
            page_text = item.get("text", "")
            page_num = item.get("page_number", 0)
            chunks = self.chunk_text(page_text)
            for i, chunk in enumerate(chunks):
                chunk_id = self._build_chunk_id(source_id, page_num, i)
                all_chunks.append(Chunk(
                    chunk_id=chunk_id,
                    page_number=page_num,
                    content=chunk,
                    content_id=chunk_id
                ))

        if all_chunks:
            texts = [chunk.content for chunk in all_chunks]
            # No fitting needed, just encoding
            embeddings = self.compute_embeddings(texts)
            for idx, emb in enumerate(embeddings):
                all_chunks[idx].embedding = emb

        return all_chunks
