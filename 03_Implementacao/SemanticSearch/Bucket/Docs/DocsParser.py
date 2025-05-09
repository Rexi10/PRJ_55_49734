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
    """Analisa o conteúdo de documentos e extrai metadados de vários formatos de ficheiro."""

    @staticmethod
    def parse_content(file_path: str) -> Dict[str, Optional[str]]:
        """
        Analisa o conteúdo e metadados de um ficheiro.

        Args:
            file_path (str): Caminho para o ficheiro do documento.

        Returns:
            Dict[str, Optional[str]]: Dicionário contendo 'content' e metadados
                                      (por exemplo, 'title', 'created_date').
        """
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
        """
        Analisa o ficheiro com base na sua extensão.

        Args:
            file_path (str): Caminho para o ficheiro.
            extension (str): Extensão do ficheiro (por exemplo, '.txt', '.pdf').

        Returns:
            tuple[str, Dict[str, Optional[str]]]: Conteúdo bruto e metadados.
        """
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
            # Conversão simples de HTML para texto
            content = re.sub(r"<[^>]+>", "", html)
            return content, metadata

        else:
            logger.warning(f"Extensão de ficheiro não suportada: {extension}")
            return "", {"error": f"Extensão de ficheiro não suportada: {extension}"}

    @staticmethod
    def _clean_content(content: str) -> str:
        """
        Limpa e normaliza o conteúdo de texto.

        Args:
            content (str): Conteúdo bruto do documento.

        Returns:
            str: Conteúdo limpo e normalizado.
        """
        if not content:
            return ""

        # Remove espaços em branco e quebras de linha excessivas
        content = re.sub(r"\s+", " ", content.strip())
        # Remove caracteres não imprimíveis
        content = re.sub(r"[^\x20-\x7E\n\t]", "", content)
        # Normaliza aspas e traços
        content = content.replace("’", "'").replace("'", "'").replace("–", "-")
        return content

    @staticmethod
    def _get_file_creation_date(file_path: str) -> Optional[str]:
        """
        Obtém a data de criação do ficheiro.

        Args:
            file_path (str): Caminho para o ficheiro.

        Returns:
            Optional[str]: Data de criação como string ou None se indisponível.
        """
        try:
            stat = os.stat(file_path)
            import datetime
            return datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()
        except Exception as e:
            logger.warning(f"Não foi possível obter a data de criação para {file_path}: {str(e)}")
            return None