import logging
from Manager import EmbeddingManager

logger = logging.getLogger(__name__)

class StartUpManager:
    def __init__(self, embedding_manager: EmbeddingManager):
        logger.debug("Initializing StartUpManager")
        self.embedding_manager = embedding_manager

    def startup(self):
        logger.info("Starting up: processing all documents")
        docs = self.embedding_manager.process_documents()
        logger.info(f"Startup completed: processed {len(docs)} documents")
        return len(docs)