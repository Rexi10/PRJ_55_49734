import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class FileManagerDAO:
    """Data Access Object
    
    ler ficheiro de texto de uma diretoria."""
    
    
    SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".md"}
    
    def get_docs(self) -> List[Dict[str, str]]:
        
        directory = "./documents"
        logger.info(f"Reading documents from {directory} and its subfolders")
        if not os.path.exists(directory):
            logger.warning(f"Directory {directory} does not exist")
            return []
        
        docs = []
        for root, _, files in os.walk(directory):
            for filename in files:
                logger.debug(f"Processing files in {root}")
                # Check if file extension is supported
                if any(filename.lower().endswith(ext) for ext in self.SUPPORTED_EXTENSIONS):
                    file_path = os.path.join(root, filename)
                    docs.append({
                        "name": filename,
                        "location": file_path,
                        "content": ""  # Content will be parsed later by DocsParser
                    })
                    logger.debug(f"Added file: {file_path}")
        
        logger.info(f"Found {len(docs)} supported files in {directory}")
        return docs