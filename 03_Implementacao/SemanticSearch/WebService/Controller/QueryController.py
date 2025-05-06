import logging
from typing import Dict, List
from Manager import QueryManager

logger = logging.getLogger(__name__)

class QueryController:
    def __init__(self, embedding_manager):
        logger.debug("Initializing QueryController")
        
        self.query_manager = QueryManager(embedding_manager)

    def handle_query(self, query: str, k: int = 3) -> Dict[str, List[Dict[str, float]]]:
        logger.debug(f"Handling query: {query} with k={k}")
        
        results = self.query_manager.process_query(query, k)
        return {"results": results}