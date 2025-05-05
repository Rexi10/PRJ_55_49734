# The `Embedder` class contains methods for generating embeddings from text and chunking content into
# smaller segments.
import logging
from typing import List
from DAO import OllamaDAO
import numpy as np

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self):
        logger.debug("Initializing Embedder")
        self.ollama_dao = OllamaDAO()
        
    def generate_embedding(self, text: str) -> np.ndarray:
        logger.debug("Calling OllamaDAO for embedding")
        return self.ollama_dao.generate_embedding(text)

    def chunk_content(self, content: str, chunk_size_words: int = 300, overlap_words: int = 150) -> List[str]:
        logger.debug(f"Chunking content (length: {len(content)} characters)")
        words = content.split()
        chunks = []
        for i in range(0, len(words) - chunk_size_words + 1, chunk_size_words - overlap_words):
            chunk_words = words[i:i + chunk_size_words]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
        if len(words) > chunk_size_words and (len(words) - i - 1) > overlap_words:
            chunk_words = words[-chunk_size_words:]
            chunks.append(' '.join(chunk_words))
        logger.debug(f"Created {len(chunks)} chunks")
        return chunks