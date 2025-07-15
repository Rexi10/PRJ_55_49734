import logging
from typing import List, Tuple
from DAO import OllamaDAO
import numpy as np
import time

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self, model: str):
        logger.debug(f"A inicializar Embedder com modelo: {model}")
        self.ollama_dao = OllamaDAO(model)

    def generate_embedding(self, text: str) -> Tuple[np.ndarray, float]:
        logger.debug("A chamar OllamaDAO para embedding")
        start_time = time.time()
        embedding = self.ollama_dao.generate_embedding(text)
        emb_time = time.time() - start_time
        return embedding, emb_time

    def chunk_content(self, content: str, chunk_size_words: int = 300, overlap_words: int = 150) -> List[str]:
        logger.debug(f"A dividir conteúdo (tamanho: {len(content)} caracteres)")
        words = content.split()
        chunks = []
        for i in range(0, len(words) - chunk_size_words + 1, chunk_size_words - overlap_words):
            chunk_words = words[i:i + chunk_size_words]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
        if len(words) > chunk_size_words and (len(words) - i - 1) > overlap_words:
            chunk_words = words[-chunk_size_words:]
            chunks.append(' '.join(chunk_words))
        logger.debug(f"Criados {len(chunks)} partes")
        return chunks