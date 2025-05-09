import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class FileManagerDAO:
    """Data Access Object for reading text files from a directory."""
    
    SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".md"}
    
    def __init__(self, directory: str = "./documents"):
        self.directory = os.getenv('BUCKET_FOLDER', directory)
    
    def get_docs(self) -> List[Dict[str, str]]:
        logger.info(f"Reading documents from {self.directory} and its subfolders")
        if not os.path.exists(self.directory):
            logger.warning(f"Directory {self.directory} does not exist")
            return []
        
        docs = []
        for root, _, files in os.walk(self.directory):
            for filename in files:
                logger.debug(f"Processing files in {root}")
                if any(filename.lower().endswith(ext) for ext in self.SUPPORTED_EXTENSIONS):
                    file_path = os.path.join(root, filename)
                    docs.append({
                        "name": filename,
                        "location": os.path.relpath(file_path, self.directory),
                        "content": ""
                    })
                    logger.debug(f"Added file: {file_path}")
        
        logger.info(f"Found {len(docs)} supported files in {self.directory}")
        return docs