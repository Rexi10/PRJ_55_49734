import logging
import numpy as np
import ollama

logger = logging.getLogger(__name__)

class OllamaDAO:
    def __init__(self):
        self.model = "nomic-embed-text"
        try:
            ollama.list()  # Check if Ollama is running
            logger.info(f"Ollama service initialized with model {self.model}")
        except Exception as e:
            logger.error("Ollama service unavailable")
            raise RuntimeError("Ollama service unavailable") from e

    def generate_embedding(self, text: str) -> np.ndarray:
        try:
            logger.debug(f"Generating embedding for text (length: {len(text)})")
            response = ollama.embeddings(model=self.model, prompt=text)
            embedding = np.array(response["embedding"], dtype=np.float32)
            logger.debug("Embedding generated successfully")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise