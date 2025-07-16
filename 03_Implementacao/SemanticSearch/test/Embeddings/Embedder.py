import requests
import logging
import time
from typing import List, Tuple

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self, model: str):
        self.model = model
        self.ollama_host = "http://ollama-test:11434"

    def chunk_content(self, content: str, chunk_size: int, overlap: int) -> List[str]:
        words = content.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def generate_embedding(self, text: str, retries: int = 3) -> Tuple[List[float], float]:
        start_time = time.time()
        for attempt in range(1, retries + 1):
            try:
                response = requests.post(
                    f"{self.ollama_host}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=30
                )
                if response.status_code == 200:
                    embedding = response.json().get("embedding", [])
                    return embedding, time.time() - start_time
                else:
                    logger.warning(
                        f"Falha ao gerar embedding com modelo {self.model}, tentativa {attempt}: "
                        f"{response.status_code} {response.reason}"
                    )
            except Exception as e:
                logger.warning(f"Falha ao gerar embedding com modelo {self.model}, tentativa {attempt}: {str(e)}")
            if attempt < retries:
                time.sleep(2 ** attempt)  # Exponential backoff
        error_msg = f"Falha ao gerar embedding com modelo {self.model} após {retries} tentativas"
        logger.error(error_msg)
        raise Exception(error_msg)

class EmbeddingRepo:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.documents = []
        self.chunks = []
        self.embeddings = []
        self.faiss_index = None

    def save(self, doc: 'Doc', chunks: List[str]):
        self.documents.append(doc)
        self.chunks.extend(chunks)
        self.embeddings.extend(doc.embeddings)
        # Placeholder for FAISS index update
        self.faiss_index = type('MockIndex', (), {'ntotal': len(self.embeddings)})()

    def search(self, query_embedding: List[float], k: int) -> List[Tuple['Doc', float, int, str]]:
        results = []
        for i, emb in enumerate(self.embeddings):
            similarity = float(np.dot(query_embedding, emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(emb)))
            results.append((self.documents[i // len(self.chunks)], similarity, i % len(self.chunks), self.chunks[i]))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]