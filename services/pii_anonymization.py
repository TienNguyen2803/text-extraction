
import asyncio
from typing import Dict, List, Any
import re

class PIIAnonymizationService:
    """Service for PII detection and anonymization using multiple libraries."""
    
    def __init__(self):
        """Initialize PII anonymization engines."""
        pass
        
    async def anonymize_text(self, text: str) -> Dict[str, Any]:
        """
        Anonymize PII in text using regex patterns.
        
        Args:
            text: Input text to anonymize
            
        Returns:
            Dictionary containing anonymized text and PII analysis
        """
        try:
            # Run PII detection and anonymization
            loop = asyncio.get_event_loop()
            
            # Find entities using regex
            entities_found = await loop.run_in_executor(
                None,
                self._find_entities_regex,
                text
            )
            
            # Anonymize text using regex
            anonymized_text = await loop.run_in_executor(
                None,
                self._anonymize_with_regex,
                text
            )
            
            return {
                "anonymized_text": anonymized_text,
                "entities_found": entities_found
            }
            
        except Exception as e:
            raise Exception(f"PII anonymization failed: {str(e)}")
    
    def _find_entities_regex(self, text: str) -> List[Dict]:
        """Find PII entities using regex patterns."""
        entities = []
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append({
                "type": "EMAIL_ADDRESS",
                "text": match.group(),
                "start_char": match.start(),
                "end_char": match.end()
            })
        
        # Phone number patterns
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\(\d{3}\)\s*\d{3}[-.]?\d{4}'
        for match in re.finditer(phone_pattern, text):
            entities.append({
                "type": "PHONE_NUMBER", 
                "text": match.group(),
                "start_char": match.start(),
                "end_char": match.end()
            })
        
        # Basic name pattern (simple heuristic)
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        for match in re.finditer(name_pattern, text):
            entities.append({
                "type": "PERSON",
                "text": match.group(),
                "start_char": match.start(),
                "end_char": match.end()
            })
        
        return entities
    
    def _anonymize_with_regex(self, text: str) -> str:
        """Anonymize text using regex patterns."""
        try:
            # Email pattern
            text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                         '[EMAIL]', text)
            
            # Phone number patterns
            text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
            text = re.sub(r'\(\d{3}\)\s*\d{3}[-.]?\d{4}', '[PHONE]', text)
            
            # Basic name pattern
            text = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[PERSON]', text)
            
            # Social Security Number pattern
            text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
            
            # Credit card patterns
            text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CREDIT_CARD]', text)
            
            # IP Address pattern
            text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_ADDRESS]', text)
            
            # URL pattern
            text = re.sub(r'https?://[^\s<>"{}|\\^`\[\]]*', '[URL]', text)
            
            return text
            
        except Exception:
            # If pattern matching fails, return original text
            return text
