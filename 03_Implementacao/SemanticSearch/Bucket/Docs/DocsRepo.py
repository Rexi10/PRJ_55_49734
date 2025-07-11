import logging
from typing import List
from DAO import FileManagerDAO
from Docs import Doc, DocsParser

logger = logging.getLogger(__name__)

class DocsRepo:
    # Inicializa repositório com FileManagerDAO
    def __init__(self):
        logger.debug("A inicializar DocsRepo")
        
        
        self.file_manager_dao = FileManagerDAO()

    def fetch_documents(self) -> List[Doc]:
        logger.info("A obter documentos de todas as subpastas")
        
        
        # Obtém documentos raw do FileManagerDAO
        raw_docs = self.file_manager_dao.get_docs()
        docs = []
        for raw_doc in raw_docs:
            parsed_data = DocsParser.parse_content(raw_doc["location"])
            if parsed_data.get("content") is None:
                logger.warning(f"A ignorar {raw_doc['name']} devido a erro de análise: {parsed_data.get('error')}")
                continue
            doc = Doc(
                name=raw_doc["name"],
                location=raw_doc["location"],
                content=parsed_data["content"]
            )
            
            # Armazena metadados, exceto conteúdo
            doc.metadata = {k: v for k, v in parsed_data.items() if k != "content"}
            docs.append(doc)
        logger.info(f"Obtidos {len(docs)} documentos")
        return docs