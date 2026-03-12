from pathlib import Path
import pdfplumber
from docx import Document


class ExtractionError(Exception):
    """Raised when text extraction fails."""
    pass


class FileHandler:
    def extract_text(self, file_path: str) -> str:
        """Extract text from a file based on its extension."""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == ".pdf":
            return self._extract_pdf(file_path)
        elif extension in [".docx", ".doc"]:
            return self._extract_docx(file_path)
        else:
            raise ExtractionError(f"Unsupported file format: {extension}")

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        try:
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n".join(text_parts)
        except Exception as e:
            raise ExtractionError(f"Failed to extract text from PDF: {str(e)}")

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n".join(paragraphs)
        except Exception as e:
            raise ExtractionError(f"Failed to extract text from DOCX: {str(e)}")

    def is_supported(self, filename: str) -> bool:
        """Check if file format is supported."""
        extension = Path(filename).suffix.lower()
        return extension in [".pdf", ".docx", ".doc"]
