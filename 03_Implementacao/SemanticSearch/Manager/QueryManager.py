import logging
from typing import List, Dict
from Manager import EmbeddingManager

logger = logging.getLogger(__name__)

class QueryManager:
    def __init__(self, embedding_manager: EmbeddingManager):
        logger.debug("Initializing QueryManager")
        self.embedding_manager = embedding_manager
        self.embedding_repo = embedding_manager.get_embedding_repo()

    def process_query(self, query: str, k: int = 3) -> List[Dict[str, float]]:
        logger.info(f"Processing query: {query} with k={k}")
        query_vector = self.embedding_manager.embedder.generate_embedding(query)
        results = self.embedding_repo.search(query_vector, k)
        result_list = [
            {
                "name": doc.name,
                "similarity": float(dist),
                "location": doc.location  # Add file path for download
            } for doc, dist in results
        ]
        logger.info(f"Query returned {len(result_list)} results")
        return result_list