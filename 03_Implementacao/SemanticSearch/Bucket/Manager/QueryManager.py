import logging
from typing import List, Dict
from Manager import EmbeddingManager

logger = logging.getLogger(__name__)

class QueryManager:
    # Inicializa com gestor de embeddings e repositório
    def __init__(self, embedding_manager: EmbeddingManager):
        logger.debug("A inicializar QueryManager")
        
        
        self.embedding_manager = embedding_manager
        self.embedding_repo = embedding_manager.get_embedding_repo()

    def process_query(self, query: str, k: int = 3) -> List[Dict[str, any]]:
        logger.info(f"A processar consulta: {query} com k={k}")


        # Gera embedding da consulta e pesquisa
        query_vector = self.embedding_manager.embedder.generate_embedding(query)
        results = self.embedding_repo.search(query_vector, k)
        result_list = []
        result_list.extend(
            {
                "name": doc.name,
                "similarity": float(dist),
                "location": doc.location,
                "chunk": chunk_text,
            }
            for doc, dist, chunk_index, chunk_text in results
        )
        logger.info(f"A Consulta retornou {len(result_list)} resultados")
        return result_list