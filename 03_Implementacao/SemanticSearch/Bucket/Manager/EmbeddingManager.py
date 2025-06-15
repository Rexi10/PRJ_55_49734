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
    # Inicializa componentes principais
    def __init__(self):
        logger.debug("A inicializar EmbeddingManager")
        
        
        self.doc_repo = DocsRepo()
        self.embedding_repo = EmbeddingRepo()
        self.embedder = Embedder()
        self.parser = DocsParser()

    def process_document(self, file_path: str) -> bool:
        logger.info(f"A processar documento em {file_path}")
        
        
        # Analisa e processa documento
        try:
            result = self.parser.parse_content(file_path)
            if result.get("content") is None:
                logger.error(f"Falha ao analisar conteúdo de {file_path}: {result.get('error', 'Erro desconhecido')}")
                return False
            content = result["content"]
            file_name = os.path.basename(file_path)
            location = file_path
            doc = Doc(name=file_name, location=location, content=content)
            doc.metadata = {k: v for k, v in result.items() if k != "content"}
            chunks = self.embedder.chunk_content(doc.content)
            doc.embeddings = [self.embedder.generate_embedding(chunk) for chunk in chunks]
            self.embedding_repo.save(doc, chunks)
            logger.info(f"Processado com sucesso {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao processar {file_path}: {str(e)}")
            return False

    def process_documents(self) -> List[Doc]:
        logger.info("A processar documentos de todas as subpastas")
        
        
        # Reinicia e processa todos os documentos
        self.embedding_repo = EmbeddingRepo()
        docs = self.doc_repo.fetch_documents()
        for doc in docs:
            chunks = self.embedder.chunk_content(doc.content)
            doc.embeddings = [self.embedder.generate_embedding(chunk) for chunk in chunks]
            self.embedding_repo.save(doc, chunks)
        logger.info(f"Processados {len(docs)} documentos com embeddings")
        return docs

    def process_query(self, query_text: str, k: int) -> Dict[str, List[Dict]]:
        logger.info(f"A processar consulta: {query_text} com k={k}")
        
        
        # Gera embedding e pesquisa resultados
        query_embedding = self.embedder.generate_embedding(query_text)
        results = self.embedding_repo.search(query_embedding, k)
        if not results:
            logger.warning("Nenhum resultado encontrado na pesquisa FAISS")
            return {"results": []}
        
        formatted_results = [
            {
                "name": doc.name,
                "location": doc.location,
                "similarity": float(similarity),
                "chunk": chunk_text,
                "chunk_index": chunk_index
            }
            for doc, similarity, chunk_index, chunk_text in results
        ]
        logger.debug(f"Consulta retornou {len(formatted_results)} resultados")
        return {"results": formatted_results}
    
    def compute_similarity(self, emb1, emb2):
        # Calcula similaridade de cosseno
        return dot(emb1, emb2) / (norm(emb1) * norm(emb2)) if norm(emb1) * norm(emb2) != 0 else 0.0

    def get_embedding_repo(self):
        return self.embedding_repo