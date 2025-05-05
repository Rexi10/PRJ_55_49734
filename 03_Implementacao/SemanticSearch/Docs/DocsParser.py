# File: DocsParser.py
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
    """Parses document content and extracts metadata from various file formats."""

    @staticmethod
    def parse_content(file_path: str) -> Dict[str, Optional[str]]:
        """
        Parse content and metadata from a file.

        Args:
            file_path (str): Path to the document file.

        Returns:
            Dict[str, Optional[str]]: Dictionary containing 'content' and metadata
                                      (e.g., 'title', 'created_date').
        """
        logger.debug(f"Parsing file: {file_path}")
        file_extension = Path(file_path).suffix.lower()
        try:
            content, metadata = DocsParser._parse_by_extension(file_path, file_extension)
            cleaned_content = DocsParser._clean_content(content)
            metadata["content"] = cleaned_content
            logger.debug(f"Successfully parsed {file_path}")
            return metadata
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {str(e)}")
            return {"content": None, "error": str(e)}

    @staticmethod
    def _parse_by_extension(file_path: str, extension: str) -> tuple[str, Dict[str, Optional[str]]]:
        """
        Parse file based on its extension.

        Args:
            file_path (str): Path to the file.
            extension (str): File extension (e.g., '.txt', '.pdf').

        Returns:
            tuple[str, Dict[str, Optional[str]]]: Raw content and metadata.
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
            # Convert Markdown to plain text
            html = markdown.markdown(content)
            # Simple HTML-to-text conversion 
            content = re.sub(r"<[^>]+>", "", html)
            return content, metadata

        else:
            logger.warning(f"Unsupported file extension: {extension}")
            return "", {"error": f"Unsupported file extension: {extension}"}

    @staticmethod
    def _clean_content(content: str) -> str:
        """
        Clean and normalize text content.

        Args:
            content (str): Raw document content.

        Returns:
            str: Cleaned and normalized content.
        """
        if not content:
            return ""

        # Remove excessive whitespace and newlines
        content = re.sub(r"\s+", " ", content.strip())
        # Remove non-printable characters
        content = re.sub(r"[^\x20-\x7E\n\t]", "", content)
        # Normalize quotes and dashes
        content = content.replace("’", "'").replace("'", "'").replace("–", "-")
        return content

    @staticmethod
    def _get_file_creation_date(file_path: str) -> Optional[str]:
        """
        Get file creation date.

        Args:
            file_path (str): Path to the file.

        Returns:
            Optional[str]: Creation date as string or None if unavailable.
        """
        try:
            stat = os.stat(file_path)
            import datetime
            return datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()
        except Exception as e:
            logger.warning(f"Could not get creation date for {file_path}: {str(e)}")
            return None