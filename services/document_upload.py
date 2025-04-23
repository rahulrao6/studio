import os
import io
import pdfminer.high_level
from docx import Document
from fastapi import UploadFile
from sqlalchemy.orm import Session

from models.contract import Contract
from core.config import settings
from utils.logging import logger
from services.document_ingestion import IngestionError
from services.document_metadata import get_document_metadata


async def process_uploaded_file(file_path: str, db: Session) -> Contract:
    """
    Processes an uploaded file (PDF, DOCX, TXT) to extract text and metadata.
    """
    try:
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == ".pdf":
            text = extract_text_from_pdf(file_path)
        elif file_extension == ".docx":
            text = extract_text_from_docx(file_path)
        elif file_extension == ".txt":
            text = extract_text_from_txt(file_path)
        else:
            raise IngestionError(f"Unsupported file type: {file_extension}")

        if not text:
            raise IngestionError("Could not extract text from the document.")

        metadata = await get_document_metadata(text)  # Extract metadata
        contract = Contract(text=text, metadata=metadata, id=-1)  # Create contract

        # Clean up temporary file
        os.remove(file_path)

        return contract
    except Exception as e:
        logger.exception("Error processing uploaded file.")
        raise IngestionError(f"Error processing file: {e}")

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        with open(pdf_path, "rb") as file:
            text = pdfminer.high_level.extract_text(file)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(docx_path: str) -> str:
    """Extracts text from a DOCX file."""
    try:
        document = Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in document.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_txt(txt_path: str) -> str:
    """Extracts text from a TXT file."""
    try:
        with open(txt_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from TXT: {e}")
        return ""
