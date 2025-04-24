from typing import Dict, Any
import os
from fastapi import UploadFile
import tempfile
import shutil
from utils.logging import logger

# Custom exception for ingestion errors
class IngestionError(Exception):
    """Exception raised for errors in the document ingestion process."""
    pass

async def ingest_document(file: UploadFile) -> Dict[str, Any]:
    """
    Ingests a document file (PDF, DOCX, etc.) and extracts its content.

    Args:
        file (UploadFile): The uploaded file to ingest.

    Returns:
        Dict[str, Any]: A dictionary containing the ingested document's metadata and content.

    Raises:
        IngestionError: If there's an error during the ingestion process.
    """
    try:
        # Create a temporary file to store the uploaded file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        # Extract file extension
        file_extension = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        
        # Process the file based on its type
        if file_extension in ['.pdf']:
            content = await extract_pdf_content(temp_file_path)
        elif file_extension in ['.docx', '.doc']:
            content = await extract_docx_content(temp_file_path)
        elif file_extension in ['.txt']:
            content = await extract_text_content(temp_file_path)
        else:
            raise IngestionError(f"Unsupported file type: {file_extension}")

        # Clean up the temporary file
        os.unlink(temp_file_path)

        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "content": content,
        }
    
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise IngestionError(f"Failed to ingest document: {str(e)}")

async def extract_pdf_content(file_path: str) -> str:
    """Extracts content from a PDF file."""
    # Placeholder - you'll need to install PyPDF2 or pdfplumber
    return "PDF content extraction placeholder"

async def extract_docx_content(file_path: str) -> str:
    """Extracts content from a DOCX file."""
    # Placeholder - you'll need to install python-docx
    return "DOCX content extraction placeholder"

async def extract_text_content(file_path: str) -> str:
    """Extracts content from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        logger.error(f"Error extracting text content: {str(e)}")
        raise IngestionError(f"Failed to extract text content: {str(e)}")