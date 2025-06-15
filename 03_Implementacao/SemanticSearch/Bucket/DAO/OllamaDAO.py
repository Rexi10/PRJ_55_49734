import logging
import numpy as np
import ollama
import os

logger = logging.getLogger(__name__)

class OllamaDAO:

    def __init__(self):
        self.model = "nomic-embed-text:v1.5"
        
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        os.environ["OLLAMA_HOST"] = ollama_host
        try:
            ollama.list()
            logger.info(f"Serviço Ollama inicializado com o modelo {self.model}")
        except Exception as e:
            logger.error("Serviço Ollama indisponível")
            raise RuntimeError("Serviço Ollama indisponível") from e

    def generate_embedding(self, text: str) -> np.ndarray:
        try:
            logger.debug(f"A gerar embedding para texto (tamanho: {len(text)})")
            
            # Gera embedding com modelo especificado
            response = ollama.embeddings(model=self.model, prompt=text)
            embedding = np.array(response["embedding"], dtype=np.float32)
            logger.debug("Embedding gerado com sucesso")
            return embedding
        
        
        # Trata de falhas na geração de embeddings
        except Exception as e:
            logger.error(f"Falha ao gerar embedding: {str(e)}")
            raise