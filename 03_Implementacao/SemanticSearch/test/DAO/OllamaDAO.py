import logging
import numpy as np
import ollama
import os
import time

logger = logging.getLogger(__name__)


class OllamaDAO:
    def __init__(self, model: str, timeout: int = 60):
        self.model = model
        self.model_with_tag = f"{model}:latest"  # Add default tag
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        os.environ["OLLAMA_HOST"] = ollama_host
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                models = ollama.list()
                logger.debug(f"Resposta de ollama.list(): {models}")
                available_models = [m.get("name", m.get("model", "")) for m in models.get("models", [])]

                # Check both with and without tag
                if self.model in available_models or self.model_with_tag in available_models:
                    logger.info(f"Serviço Ollama inicializado com o modelo {self.model}")
                    return

                logger.debug(f"Modelo {self.model} ainda não disponível, aguardando...")
                time.sleep(2)

            logger.error(
                f"Modelo {self.model} não encontrado após {timeout} segundos. Modelos disponíveis: {available_models}")
            raise RuntimeError(f"Modelo {self.model} não encontrado no servidor Ollama")
        except Exception as e:
            logger.error(f"Serviço Ollama indisponível para modelo {self.model}: {str(e)}")
            raise RuntimeError(f"Serviço Ollama indisponível para modelo {self.model}") from e

    def generate_embedding(self, text: str) -> np.ndarray:
        if not text.strip():
            logger.error("Tentativa de gerar embedding para texto vazio")
            raise ValueError("Texto de entrada está vazio")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.debug(f"A gerar embedding para texto (tamanho: {len(text)}) com modelo {self.model}")
                # Try both model names
                try:
                    response = ollama.embeddings(model=self.model, prompt=text)
                except:
                    response = ollama.embeddings(model=self.model_with_tag, prompt=text)

                if "embedding" not in response:
                    logger.error(f"Resposta do Ollama não contém 'embedding': {response}")
                    raise ValueError("Resposta do Ollama não contém 'embedding'")
                embedding = np.array(response["embedding"], dtype=np.float32)
                logger.debug(f"Embedding gerado com sucesso, dimensão: {len(embedding)}")
                return embedding
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Falha ao gerar embedding com modelo {self.model}, tentativa {attempt + 1}: {str(e)}")
                    time.sleep(2)
                else:
                    logger.error(
                        f"Falha ao gerar embedding com modelo {self.model} após {max_retries} tentativas: {str(e)}")
                    raise