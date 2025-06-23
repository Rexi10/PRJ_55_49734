import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


#Objeto de acesso a dados para leitura de ficheiros de texto de um diretoria.    
class FileManagerDAO:

    
    
    SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".md"}
    
    # Inicializa com o diretoria padr�o
    def __init__(self, directory: str = "./documents"):
        self.directory = os.getenv('BUCKET_FOLDER', directory)
    
    def get_docs(self) -> List[Dict[str, str]]:
        logger.info(f"A ler documentos de {self.directory} e subpastas")
        
        
        # Verifica se o diretoria existe
        if not os.path.exists(self.directory):
            logger.error(f"Diretório {self.directory} não existe")
            return []
        
        docs = []
        for root, _, files in os.walk(self.directory):
            for filename in files:
                logger.debug(f"A processar ficheiros em {root}")
                if any(filename.lower().endswith(ext) for ext in self.SUPPORTED_EXTENSIONS):
                    file_path = os.path.join(root, filename)
                    docs.append({
                        "name": filename,
                        "location": os.path.relpath(file_path, self.directory),
                        "content": ""
                    })
                    logger.debug(f"Ficheiro adicionado: {file_path}")
                    
                    
        # Regista o numero de ficheiros encontrados
        logger.info(f"Encontrados {len(docs)} ficheiros suportados em {self.directory}")
        return docs