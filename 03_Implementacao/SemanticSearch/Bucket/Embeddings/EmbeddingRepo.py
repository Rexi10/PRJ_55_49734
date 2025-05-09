import logging
import numpy as np
import faiss
from typing import List, Tuple
from Docs.Doc import Doc

logger = logging.getLogger(__name__)

class EmbeddingRepo:
    def __init__(self):
        logger.debug("Initializing EmbeddingRepo")
        self.faiss_index = faiss.IndexFlatIP(768)
        self.docs = []  # Stores (doc, chunk_index, chunk_text) tuples

    def save(self, doc: Doc, chunks: List[str] = None):
        logger.debug(f"Saving embeddings for document: {doc.name}")
        for i, embedding in enumerate(doc.embeddings):
            norm = np.linalg.norm(embedding)
            normalized_embedding = embedding / norm if norm != 0 else embedding
            self.faiss_index.add(np.array([normalized_embedding]))
            chunk_text = chunks[i] if chunks and i < len(chunks) else ""
            self.docs.append((doc, i, chunk_text))
        logger.debug(f"Saved {len(doc.embeddings)} embeddings")

    def search(self, query_vector: np.ndarray, k: int = 3) -> List[Tuple[Doc, float, int, str]]:
        if self.faiss_index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return []
        logger.debug(f"Searching FAISS index with k={k}")
        norm = np.linalg.norm(query_vector)
        normalized_query = query_vector / norm if norm != 0 else query_vector
        search_k = min(k * 2, self.faiss_index.ntotal)
        distances, indices = self.faiss_index.search(np.array([normalized_query]), search_k)
        similarities = distances[0]
        results = []
        seen_docs = set()
        for j, i in enumerate(indices[0]):
            if len(results) >= k:
                break
            doc, chunk_index, chunk_text = self.docs[i]
            if doc.name not in seen_docs:
                results.append((doc, similarities[j], chunk_index, chunk_text))
                seen_docs.add(doc.name)
        logger.debug(f"Found {len(results)} unique documents")
        return results