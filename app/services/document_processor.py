from pathlib import Path

from docx import Document
from pypdf import PdfReader


class DocumentProcessor:
    def extract_text(self, file_path: str) -> str:
        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return self._read_pdf(file_path)

        elif extension == ".txt":
            return self._read_txt(file_path)

        elif extension == ".docx":
            return self._read_docx(file_path)

        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def _read_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            text += page.extract_text() + "\n"

        return text

    def _read_txt(self, file_path: str) -> str:
        with open(file_path, encoding="utf-8") as f:
            return f.read()

    def _read_docx(self, file_path: str) -> str:
        document = Document(file_path)

        return "\n".join(paragraph.text for paragraph in document.paragraphs)
