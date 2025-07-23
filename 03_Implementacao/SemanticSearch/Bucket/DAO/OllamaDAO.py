import logging
import numpy as np
import ollama
import os
import time

logger = logging.getLogger(__name__)

class OllamaDAO:
    def __init__(self):
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        os.environ["OLLAMA_HOST"] = ollama_host
        try:
            # Get the list of available models from Ollama
            models = ollama.list().get("models", [])
            if not models:
                logger.error("No models available in Ollama service")
                raise RuntimeError("No models available in Ollama service")
            # Select the first model from the list (assuming models.txt has at least one model)
            self.model = models[0]["model"]  # Changed from "name" to "model"
            logger.info(f"Ollama service initialized with model {self.model}")
        except Exception as e:
            logger.error("Ollama service unavailable")
            raise RuntimeError("Ollama service unavailable") from e

    def generate_embedding(self, text: str) -> np.ndarray:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.debug(f"Generating embedding for text (length: {len(text)})")
                response = ollama.embeddings(model=self.model, prompt=text)
                embedding = np.array(response["embedding"], dtype=np.float32)
                logger.debug("Embedding generated successfully")
                return embedding
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to generate embedding, attempt {attempt + 1}: {str(e)}")
                    time.sleep(2)
                else:
                    logger.error(f"Failed to generate embedding after {max_retries} attempts: {str(e)}")
                    raise