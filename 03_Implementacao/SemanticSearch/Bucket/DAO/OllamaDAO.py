import logging
import numpy as np
import ollama
import os

logger = logging.getLogger(__name__)

class OllamaDAO:

    def __init__(self):
        self.model = "oscardp96/medcpt-query-article"
        
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        os.environ["OLLAMA_HOST"] = ollama_host
        try:
            ollama.list()
            logger.info(f"ServiÃ§o Ollama inicializado com o modelo {self.model}")
        except Exception as e:
            logger.error("ServiÃ§o Ollama indisponÃ­vel")
            raise RuntimeError("ServiÃ§o Ollama indisponÃ­vel") from e

    def generate_embedding(self, text: str) -> np.ndarray:
        try:
            logger.debug(f"A gerar embedding para texto (tamanho: {len(text)})")
            
            # Gera embedding com modelo especificado
            response = ollama.embeddings(model=self.model, prompt=text)
            embedding = np.array(response["embedding"], dtype=np.float32)
            logger.debug("Embedding gerado com sucesso")
            return embedding
        
        
        # Trata de falhas na geraÃ§Ã£o de embeddings
        except Exception as e:
            logger.error(f"Falha ao gerar embedding: {str(e)}")
            raise