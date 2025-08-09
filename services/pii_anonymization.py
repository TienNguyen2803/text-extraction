
import asyncio
from typing import Dict, List, Any
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import scrubadub
import re

class PIIAnonymizationService:
    """Service for PII detection and anonymization using multiple libraries."""
    
    def __init__(self):
        """Initialize PII anonymization engines."""
        self.presidio_analyzer = AnalyzerEngine()
        self.presidio_anonymizer = AnonymizerEngine()
        self.scrubadub_scrubber = scrubadub.Scrubber()
        
    async def anonymize_text(self, text: str) -> Dict[str, Any]:
        """
        Anonymize PII in text using multiple libraries.
        
        Args:
            text: Input text to anonymize
            
        Returns:
            Dictionary containing anonymized text and PII analysis
        """
        try:
            # Run PII detection and anonymization in thread pool
            loop = asyncio.get_event_loop()
            
            # Presidio analysis
            presidio_results = await loop.run_in_executor(
                None, 
                self._analyze_with_presidio, 
                text
            )
            
            # Anonymize with Presidio
            presidio_anonymized = await loop.run_in_executor(
                None,
                self._anonymize_with_presidio,
                text,
                presidio_results
            )
            
            # Additional anonymization with Scrubadub
            scrubadub_anonymized = await loop.run_in_executor(
                None,
                self._anonymize_with_scrubadub,
                presidio_anonymized
            )
            
            # Additional anonymization with anonympy patterns
            final_anonymized = await loop.run_in_executor(
                None,
                self._anonymize_with_anonympy,
                scrubadub_anonymized
            )
            
            # Convert Presidio results to our format
            entities_found = []
            for result in presidio_results:
                entities_found.append({
                    "type": result.entity_type,
                    "text": text[result.start:result.end],
                    "start_char": result.start,
                    "end_char": result.end
                })
            
            return {
                "anonymized_text": final_anonymized,
                "entities_found": entities_found
            }
            
        except Exception as e:
            raise Exception(f"PII anonymization failed: {str(e)}")
    
    def _analyze_with_presidio(self, text: str):
        """Analyze text with Presidio for PII detection."""
        return self.presidio_analyzer.analyze(
            text=text,
            language='en',
            entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", 
                     "SSN", "IBAN_CODE", "IP_ADDRESS", "DATE_TIME", "LOCATION",
                     "ORGANIZATION", "URL"]
        )
    
    def _anonymize_with_presidio(self, text: str, analyzer_results):
        """Anonymize text using Presidio."""
        anonymized_result = self.presidio_anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results
        )
        return anonymized_result.text
    
    def _anonymize_with_scrubadub(self, text: str) -> str:
        """Additional anonymization using Scrubadub."""
        try:
            return self.scrubadub_scrubber.clean(text)
        except Exception:
            # If scrubadub fails, return original text
            return text
    
    def _anonymize_with_anonympy(self, text: str) -> str:
        """Additional anonymization using anonympy-style patterns."""
        try:
            # Implement basic anonympy-style patterns
            # Email pattern
            text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                         '[EMAIL]', text)
            
            # Phone number patterns
            text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
            text = re.sub(r'\(\d{3}\)\s*\d{3}[-.]?\d{4}', '[PHONE]', text)
            
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
