"""PHI (Protected Health Information) redaction utilities for HIPAA compliance."""

import re
from typing import Dict, List, Tuple


class PHIRedactor:
    """Redacts PHI from text to ensure HIPAA compliance."""
    
    # Patterns for common PHI elements
    PATTERNS = {
        # Social Security Numbers
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b",
        # Phone Numbers
        "phone": r"\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b|\(\d{3}\)\s*\d{3}[-.\s]??\d{4}\b",
        # Email Addresses
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        # Medical Record Numbers (MRN) - assuming format MRN followed by digits
        "mrn": r"\bMRN[:\s#]?\d{6,10}\b",
        # Patient ID
        "patient_id": r"\b[Pp]atient[:\s#]?ID[:\s#]?\d{6,10}\b",
        # Insurance Policy Numbers
        "policy": r"\b[Pp]olicy[:\s#]?\d{8,12}\b",
        # Credit Card Numbers
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        # Dates (birth dates, etc.)
        "date": r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",
    }
    
    def __init__(self, enable_detailed_logging: bool = False):
        """Initialize the PHI redactor.
        
        Args:
            enable_detailed_logging: If True, logs what was redacted (for debugging only)
        """
        self.enable_detailed_logging = enable_detailed_logging
        self.redaction_stats: Dict[str, int] = {}
    
    def redact(self, text: str, patterns: List[str] = None) -> Tuple[str, Dict[str, int]]:
        """Redact PHI from text.
        
        Args:
            text: Text to redact
            patterns: List of pattern names to use. If None, uses all patterns.
            
        Returns:
            Tuple of (redacted_text, redaction_counts)
        """
        if text is None or text == "":
            return text, {}
        
        redacted_text = text
        redaction_counts = {}
        
        patterns_to_use = patterns or list(self.PATTERNS.keys())
        
        for pattern_name in patterns_to_use:
            if pattern_name in self.PATTERNS:
                pattern = self.PATTERNS[pattern_name]
                matches = re.findall(pattern, redacted_text, re.IGNORECASE)
                count = len(matches)
                
                if count > 0:
                    redaction_counts[pattern_name] = count
                    replacement = f"[REDACTED_{pattern_name.upper()}]"
                    redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)
        
        return redacted_text, redaction_counts
    
    def redact_dict(self, data: Dict, keys_to_redact: List[str] = None) -> Dict:
        """Redact PHI from dictionary values.
        
        Args:
            data: Dictionary to redact
            keys_to_redact: Specific keys to redact. If None, redacts all string values.
            
        Returns:
            Dictionary with redacted values
        """
        if not data:
            return data
        
        redacted_data = data.copy()
        
        for key, value in redacted_data.items():
            if keys_to_redact and key not in keys_to_redact:
                continue
                
            if isinstance(value, str):
                redacted_data[key], _ = self.redact(value)
            elif isinstance(value, dict):
                redacted_data[key] = self.redact_dict(value, keys_to_redact)
            elif isinstance(value, list):
                redacted_data[key] = [
                    self.redact(item)[0] if isinstance(item, str) else item
                    for item in value
                ]
        
        return redacted_data
    
    def is_text_safe(self, text: str) -> bool:
        """Check if text contains PHI.
        
        Args:
            text: Text to check
            
        Returns:
            True if no PHI detected, False otherwise
        """
        _, counts = self.redact(text)
        return len(counts) == 0


# Singleton instance
phi_redactor = PHIRedactor()
