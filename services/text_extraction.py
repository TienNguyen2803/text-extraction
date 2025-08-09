import asyncio
import tempfile
import os
from typing import Optional
from unstructured.partition.auto import partition

class TextExtractionService:
    """Service for extracting text from documents using unstructured library."""

    def __init__(self):
        """Initialize the text extraction service."""
        pass

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
        Fallback to unstructured for marker strategy.

        Args:
            file_content: Raw file content
            filename: Original filename

        Returns:
            Extracted text using unstructured
        """
        # Since marker has issues, fallback to unstructured
        return await self.extract_with_unstructured(file_content, filename)

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename."""
        return os.path.splitext(filename)[1] or '.txt'