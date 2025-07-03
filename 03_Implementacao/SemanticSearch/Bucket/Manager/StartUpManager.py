import logging
from Manager import EmbeddingManager

logger = logging.getLogger(__name__)

class StartUpManager:
    # Inicializa com gestor de embeddings
    def __init__(self, embedding_manager: EmbeddingManager):
        logger.debug("A inicializar StartUpManager")
        
        
        self.embedding_manager = embedding_manager

    def startup(self) -> int:
        logger.info("A iniciar: a processar todos os documentos")
        
        
        # Processa todos os documentos
        docs = self.embedding_manager.process_documents()
        logger.info(f"inicialização concluí­da: processados {len(docs)} documentos")
        return len(docs)