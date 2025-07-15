import logging
import numpy as np
import ollama
import os

logger = logging.getLogger(__name__)

class OllamaDAO:
    def __init__(self):
        self.model = "nomic-embed-text"
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        os.environ["OLLAMA_HOST"] = ollama_host
        try:
            ollama.list()
            logger.info(f"Serviço Ollama inicializado com o modelo {self.model}")
        except Exception as e:
            logger.error("Serviço Ollama indisponível")
            raise RuntimeError("Serviço Ollama indisponível") from e

    # In OllamaDAO.py, modify generate_embedding
    def generate_embedding(self, text: str) -> np.ndarray:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.debug(f"A gerar embedding para texto (tamanho: {len(text)})")
                response = ollama.embeddings(model=self.model, prompt=text)
                embedding = np.array(response["embedding"], dtype=np.float32)
                logger.debug("Embedding gerado com sucesso")
                return embedding
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Falha ao gerar embedding, tentativa {attempt + 1}: {str(e)}")
                    time.sleep(2)
                else:
                    logger.error(f"Falha ao gerar embedding após {max_retries} tentativas: {str(e)}")
                    raise