import os
from typing import List, Dict, Any, Optional
import PyPDF2
from utils.logging import get_logger

logger = get_logger(__name__)

class DocumentProcessor:
    """
    Service for processing and ingesting documents into the system.
    """
    
    def __init__(self, storage_path: str = "./uploads"):
        """
        Initialize the document processor.
        
        Args:
            storage_path: Directory to store uploaded documents
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
    def save_document(self, file_content: bytes, filename: str) -> str:
        """
        Save an uploaded document to disk.
        
        Args:
            file_content: Binary content of the file
            filename: Name of the file
            
        Returns:
            The path where the file was saved
        """
        file_path = os.path.join(self.storage_path, filename)
        
        with open(file_path, "wb") as f:
            f.write(file_content)
            
        logger.info(f"Document saved: {filename}")
        return file_path
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        text = ""
        
        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                    
            logger.info(f"Text extracted from PDF: {file_path}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document for analysis.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Processed document data
        """
        # Determine file type and extract accordingly
        if file_path.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        else:
            # Add support for other file types as needed
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        # Basic document metadata
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        document_data = {
            "filename": filename,
            "file_path": file_path,
            "file_size": file_size,
            "text_content": text,
            # Add more metadata as needed
        }
        
        logger.info(f"Document processed: {filename}")
        return document_data

# Create a singleton instance
document_processor = DocumentProcessor()