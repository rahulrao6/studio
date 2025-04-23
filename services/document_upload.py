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

# This module handles the process of uploading and extracting text from various document types.

async def process_uploaded_file(file_path: str, db: Session) -> Contract:
    """
    Processes an uploaded file (PDF, DOCX, TXT) to extract text and metadata.

    Args:
        file_path (str): The path to the uploaded file.
        db (Session): The database session.

    Returns:
        Contract: A Contract object containing the extracted text and metadata.

    Raises:
        IngestionError: If the file type is unsupported or if text extraction fails.

    To alter this function:
    1. Add support for more file types by adding new `elif` blocks.
    2. Modify the `extract_text_from_pdf`, `extract_text_from_docx`, and `extract_text_from_txt` functions to improve text extraction.
    3. Change the logic for extracting specific metadata fields.

    To improve the accuracy of this function:
    1. Improve the text extraction logic for each file type.
    2. Improve the metadata extraction logic.
    """
    try:
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == ".pdf":
            text = extract_text_from_pdf(file_path) # Calls function to extract text from PDF
        elif file_extension == ".docx":
            text = extract_text_from_docx(file_path) # Calls function to extract text from DOCX
        elif file_extension == ".txt":
            text = extract_text_from_txt(file_path) # Calls function to extract text from TXT
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
    """Extracts text from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF file.

    To alter this function:
    1. Use a different PDF extraction library.
    2. Add logic to handle different PDF encodings.
    3. Add logic to extract text from images in the PDF.

    To improve the accuracy of this function:
    1. Experiment with different PDF extraction parameters.
    2. Implement error handling for specific PDF extraction errors.
    """
    try:
        with open(pdf_path, "rb") as file:
            text = pdfminer.high_level.extract_text(file)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(docx_path: str) -> str:
    """Extracts text from a DOCX file.

    Args:
        docx_path (str): The path to the DOCX file.

    Returns:
        str: The extracted text from the DOCX file.

    To alter this function:
    1. Use a different DOCX extraction library.
    2. Add logic to handle different DOCX versions.
    3. Add logic to extract text from tables and other complex elements in the DOCX.

    To improve the accuracy of this function:
    1. Implement error handling for specific DOCX extraction errors.
    2. Implement logic to handle different DOCX formatting styles.
    """
    try:
        document = Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in document.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_txt(txt_path: str) -> str:
    """Extracts text from a TXT file.

    Args:
        txt_path (str): The path to the TXT file.

        Returns:
            str: The extracted text from the TXT file.

        To alter this function:
        1. Use a different text encoding.
        2. Add logic to handle different line endings.

        To improve the accuracy of this function:
        1. Implement error handling for specific TXT extraction errors.
        2. Implement logic to handle different text formatting styles.
    """
    try:
        with open(txt_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from TXT: {e}")
        return ""
