
import asyncio
import tempfile
import os
from typing import Optional
from unstructured.partition.auto import partition
import marker
from marker.convert import convert_single_pdf
from marker.models import load_all_models

class TextExtractionService:
    """Service for extracting text from documents using unstructured and marker libraries."""
    
    def __init__(self):
        """Initialize the text extraction service."""
        self.marker_models = None
    
    async def extract_with_unstructured(self, file_content: bytes, filename: str) -> str:
        """
        Extract text using unstructured library.
        
        Args:
            file_content: Raw file content
            filename: Original filename
            
        Returns:
            Extracted text with layout preservation
        """
        try:
            # Write content to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=self._get_file_extension(filename)) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
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
            
        except Exception as e:
            raise Exception(f"Unstructured extraction failed: {str(e)}")
    
    async def extract_with_marker(self, file_content: bytes, filename: str) -> str:
        """
        Extract text using marker library for high-fidelity PDF to Markdown conversion.
        
        Args:
            file_content: Raw file content
            filename: Original filename
            
        Returns:
            Extracted text in Markdown format
        """
        try:
            # Check if file is PDF
            if not filename.lower().endswith('.pdf'):
                # Fall back to unstructured for non-PDF files
                return await self.extract_with_unstructured(file_content, filename)
            
            # Load marker models if not already loaded
            if self.marker_models is None:
                loop = asyncio.get_event_loop()
                self.marker_models = await loop.run_in_executor(None, load_all_models)
            
            # Write content to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            # Run marker conversion in thread pool
            loop = asyncio.get_event_loop()
            full_text, images, out_meta = await loop.run_in_executor(
                None, 
                convert_single_pdf,
                temp_file_path,
                self.marker_models
            )
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return full_text
            
        except Exception as e:
            # Fall back to unstructured if marker fails
            return await self.extract_with_unstructured(file_content, filename)
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename."""
        return os.path.splitext(filename)[1] or '.txt'
