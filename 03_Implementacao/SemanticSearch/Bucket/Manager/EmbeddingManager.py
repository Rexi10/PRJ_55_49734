import logging
import os
from numpy import dot
from numpy.linalg import norm

from typing import List, Dict
from Docs import DocsRepo, Doc
from Embeddings import EmbeddingRepo, Embedder
from Docs import DocsParser

logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self):
        logger.debug("Initializing EmbeddingManager")
        self.doc_repo = DocsRepo()
        self.embedding_repo = EmbeddingRepo()
        self.embedder = Embedder()
        self.parser = DocsParser()  # Initialize DocsParser

    def process_document(self, file_path: str) -> bool:
        logger.info(f"Processing document at {file_path}")
        try:
            result = self.parser.parse_content(file_path)
            if result.get("content") is None:
                logger.error(f"Failed to parse content from {file_path}: {result.get('error', 'Unknown error')}")
                return False
            content = result["content"]
            file_name = os.path.basename(file_path)
            location = file_path
            doc = Doc(name=file_name, location=location, content=content)
            doc.metadata = {k: v for k, v in result.items() if k != "content"}
            chunks = self.embedder.chunk_content(doc.content)
            doc.embeddings = [self.embedder.generate_embedding(chunk) for chunk in chunks]
            self.embedding_repo.save(doc, chunks)
            logger.info(f"Successfully processed {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return False

    def process_documents(self) -> List[Doc]:
        logger.info("Processing documents from all subfolders")
        self.embedding_repo.reset()
        docs = self.doc_repo.fetch_documents()
        for doc in docs:
            chunks = self.embedder.chunk_content(doc.content)
            doc.embeddings = [self.embedder.generate_embedding(chunk) for chunk in chunks]
            self.embedding_repo.save(doc, chunks)
        logger.info(f"Processed {len(docs)} documents with embeddings")
        return docs

    def process_query(self, query_text: str, k: int) -> Dict[str, List[Dict]]:
        logger.info(f"Processing query: {query_text} with k={k}")
        query_embedding = self.embedder.generate_embedding(query_text)
        results = self.embedding_repo.search(query_embedding, k)
        if not results:
            logger.warning("No results found in FAISS search")
            return {"results": []}
        
        formatted_results = [
            {
                "name": doc.name,
                "location": doc.location,
                "similarity": float(similarity),
                "chunk": chunk_text,  # Return full chunk text
                "chunk_index": chunk_index
            }
            for doc, similarity, chunk_index, chunk_text in results
        ]
        logger.debug(f"Query returned {len(formatted_results)} results")
        return {"results": formatted_results}
    
    
    def compute_similarity(self, emb1, emb2):
        return dot(emb1, emb2) / (norm(emb1) * norm(emb2)) if norm(emb1) * norm(emb2) != 0 else 0.0

    def get_embedding_repo(self):
        return self.embedding_repo