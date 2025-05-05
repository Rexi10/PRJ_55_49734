import logging
from typing import List
from Docs import DocsRepo, Doc
from Embeddings import EmbeddingRepo, Embedder


logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self):
        logger.debug("Initializing EmbeddingManager")
        self.doc_repo = DocsRepo()
        self.embedding_repo = EmbeddingRepo()
        self.embedder = Embedder()

    def process_documents(self) -> List[Doc]:
        logger.info("Processing documents from all subfolders")
        self.embedding_repo.reset()
        docs = self.doc_repo.fetch_documents()
        for doc in docs:
            chunks = self.embedder.chunk_content(doc.content)
            doc.embeddings = [self.embedder.generate_embedding(chunk) for chunk in chunks]
            self.embedding_repo.save(doc)
        logger.info(f"Processed {len(docs)} documents with embeddings")
        return docs

    def get_embedding_repo(self):
        return self.embedding_repo