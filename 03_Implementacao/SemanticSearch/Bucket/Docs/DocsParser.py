# Ficheiro: DocsParser.py
import logging
import re
from typing import Dict, Optional
from pathlib import Path
import os
import PyPDF2
from docx import Document
import markdown

logger = logging.getLogger(__name__)

class DocsParser:
    #  Analisa o conteúdo de documentos e extrai metadados de vários formatos de ficheiro.

    @staticmethod
    def parse_content(file_path: str) -> Dict[str, Optional[str]]:
        
        # Analisa o conteúdo e metadados de um ficheiro.
        
        logger.debug(f"A analisar ficheiro: {file_path}")
        file_extension = Path(file_path).suffix.lower()
        try:
            content, metadata = DocsParser._parse_by_extension(file_path, file_extension)
            cleaned_content = DocsParser._clean_content(content)
            metadata["content"] = cleaned_content
            logger.debug(f"Ficheiro {file_path} analisado com sucesso")
            return metadata
        except Exception as e:
            logger.error(f"Falha ao analisar {file_path}: {str(e)}")
            return {"content": None, "error": str(e)}

    @staticmethod
    def _parse_by_extension(file_path: str, extension: str) -> tuple[str, Dict[str, Optional[str]]]:

        # Analisa o ficheiro com base na sua estensão.

        metadata = {
            "title": Path(file_path).stem,
            "created_date": DocsParser._get_file_creation_date(file_path),
            "extension": extension
        }

        if extension == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content, metadata

        elif extension == ".pdf":
            with open(file_path, "rb") as f:
                pdf = PyPDF2.PdfReader(f)
                content = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            metadata["page_count"] = len(pdf.pages)
            return content, metadata

        elif extension == ".docx":
            doc = Document(file_path)
            content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            return content, metadata

        elif extension == ".md":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Converte Markdown para texto simples
            html = markdown.markdown(content)
            # ConversÃ£o simples de HTML para texto
            content = re.sub(r"<[^>]+>", "", html)
            return content, metadata

        else:
            logger.warning(f"ExtensÃ£o de ficheiro nÃ£o suportada: {extension}")
            return "", {"error": f"ExtensÃ£o de ficheiro nÃ£o suportada: {extension}"}

    @staticmethod
    def _clean_content(content: str) -> str:

        # Limpa e normaliza o conteúdo de texto.

        if not content:
            return ""

        # Remove espaÃ§os em branco e quebras de linha excessivas
        content = re.sub(r"\s+", " ", content.strip())
        # Remove caracteres nÃ£o imprimÃ­veis
        content = re.sub(r"[^\x20-\x7E\n\t]", "", content)
        # Normaliza aspas e traÃ§os
        content = content.replace("â", "'").replace("'", "'").replace("â", "-")
        return content

    @staticmethod
    def _get_file_creation_date(file_path: str) -> Optional[str]:

        # Obtem a data de criação do ficheiro.

        try:
            stat = os.stat(file_path)
            import datetime
            return datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()
        except Exception as e:
            logger.warning(f"NÃ£o foi possÃ­vel obter a data de criaÃ§Ã£o para {file_path}: {str(e)}")
            return None