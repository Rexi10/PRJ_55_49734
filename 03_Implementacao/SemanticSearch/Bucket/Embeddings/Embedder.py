import logging
from typing import List
from DAO import OllamaDAO
import numpy as np

logger = logging.getLogger(__name__)

class Embedder:
    # Inicializa com DAO para embeddings
    def __init__(self):
        logger.debug("A inicializar Embedder")
        
        
        self.ollama_dao = OllamaDAO()
        
    def generate_embedding(self, text: str) -> np.ndarray:
        logger.debug("A chamar OllamaDAO para embedding")
        
        
        return self.ollama_dao.generate_embedding(text)
    

    def chunk_content(self, content: str, chunk_size_words: int = 300, overlap_words: int = 150) -> List[str]:
        # Divide conteÃºdo em partes com sobreposiÃ§Ã£o
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