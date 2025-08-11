import asyncio
import tempfile
import os
from typing import Optional
from PIL import Image
import pytesseract

# Configure tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Set partition to None to force fallback
partition = None

import pdfplumber
from PyPDF2 import PdfReader

class TextExtractionService:
    """Service for extracting text from documents using unstructured library."""

    def __init__(self):
        """Initialize the text extraction service."""
        pass

    async def extract_with_unstructured(self, file_content: bytes, filename: str) -> str:
        """
        Extract text using unstructured library with fallback.

        Args:
            file_content: Raw file content
            filename: Original filename

        Returns:
            Extracted text with layout preservation
        """
        try:
            # If unstructured is not available or fails, use fallback
            if partition is None:
                return await self._fallback_extraction(file_content, filename)
                
            # Write content to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=self._get_file_extension(filename)) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                # Run extraction in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                elements = await loop.run_in_executor(None, partition, temp_file_path)

                # Clean up temporary file
                os.unlink(temp_file_path)

                # Convert elements to text while preserving structure
                extracted_text = ""
                for element in elements:
                    text = str(element)
                    # Add spacing based on element type to preserve layout
                    if hasattr(element, 'category'):
                        if element.category in ['Title', 'Header']:
                            extracted_text += f"\n# {text}\n\n"
                        elif element.category == 'Table':
                            extracted_text += f"\n{text}\n\n"
                        elif element.category == 'ListItem':
                            extracted_text += f"- {text}\n"
                        else:
                            extracted_text += f"{text}\n\n"
                    else:
                        extracted_text += f"{text}\n\n"

                return extracted_text.strip()
                
            except Exception:
                # Clean up temporary file if error occurs
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                # Fallback to alternative extraction
                return await self._fallback_extraction(file_content, filename)

        except Exception as e:
            # Final fallback
            return await self._fallback_extraction(file_content, filename)

    async def extract_with_marker(self, file_content: bytes, filename: str) -> str:
        """
        Fallback to unstructured for marker strategy.

        Args:
            file_content: Raw file content
            filename: Original filename

        Returns:
            Extracted text using unstructured
        """
        # Since marker has issues, fallback to unstructured
        return await self.extract_with_unstructured(file_content, filename)

    async def _fallback_extraction(self, file_content: bytes, filename: str) -> str:
        """
        Fallback text extraction for when unstructured fails.
        
        Args:
            file_content: Raw file content
            filename: Original filename
            
        Returns:
            Extracted text using alternative methods
        """
        try:
            file_ext = self._get_file_extension(filename).lower()
            
            if file_ext == '.pdf':
                return await self._extract_pdf_fallback(file_content)
            elif file_ext in ['.txt', '.md']:
                return file_content.decode('utf-8', errors='ignore')
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp']:
                return await self._extract_image_text(file_content)
            else:
                # For other file types, try to decode as text
                return file_content.decode('utf-8', errors='ignore')
                
        except Exception:
            return "Error: Could not extract text from the document."
    
    async def _extract_pdf_fallback(self, file_content: bytes) -> str:
        """Extract text from PDF using pdfplumber and PyPDF2 as fallback."""
        try:
            # Try pdfplumber first
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                loop = asyncio.get_event_loop()
                text = await loop.run_in_executor(None, self._pdfplumber_extract, temp_file_path)
                os.unlink(temp_file_path)
                return text
            except Exception:
                # Fallback to PyPDF2
                try:
                    text = await loop.run_in_executor(None, self._pypdf2_extract, temp_file_path)
                    os.unlink(temp_file_path)
                    return text
                except Exception:
                    os.unlink(temp_file_path)
                    return "Error: Could not extract text from PDF."
                    
        except Exception:
            return "Error: Could not process PDF file."
    
    def _pdfplumber_extract(self, file_path: str) -> str:
        """Extract text using pdfplumber."""
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            return text.strip()
    
    def _pypdf2_extract(self, file_path: str) -> str:
        """Extract text using PyPDF2."""
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return text.strip()

    async def _extract_image_text(self, file_content: bytes) -> str:
        """Extract text from image using OCR."""
        try:
            # Check if tesseract is available
            try:
                pytesseract.get_tesseract_version()
            except Exception:
                return "Error: Tesseract OCR is not installed or configured properly. Please install tesseract-ocr package."
            
            # Write content to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                # Open image with PIL
                image = Image.open(temp_file_path)
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Run OCR in thread pool with basic English first
                loop = asyncio.get_event_loop()
                try:
                    # Try with Vietnamese + English
                    extracted_text = await loop.run_in_executor(
                        None, 
                        pytesseract.image_to_string, 
                        image,
                        'vie+eng'
                    )
                except Exception:
                    # Fallback to English only
                    extracted_text = await loop.run_in_executor(
                        None, 
                        pytesseract.image_to_string, 
                        image,
                        'eng'
                    )
                
                # Clean up
                os.unlink(temp_file_path)
                
                if extracted_text.strip():
                    return extracted_text.strip()
                else:
                    return "No text found in the image."
                    
            except Exception as e:
                # Clean up temporary file if error occurs
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                return f"Error extracting text from image: {str(e)}"
                
        except Exception as e:
            return f"Error processing image file: {str(e)}"

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename."""
        return os.path.splitext(filename)[1] or '.txt'