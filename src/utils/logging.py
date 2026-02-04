"""Logging utilities with HIPAA compliance."""

import logging
import json
from typing import Any, Dict, Optional

try:
    from google.cloud import logging as cloud_logging
except ImportError:
    cloud_logging = None

from .  import utcnow


class HIPAACompliantLogger:
    """Logger that ensures no PHI is logged."""
    
    def __init__(self, name: str, enable_cloud_logging: bool = False):
        """Initialize logger.
        
        Args:
            name: Logger name
            enable_cloud_logging: If True, also logs to Google Cloud Logging
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Cloud logging client (optional)
        self.cloud_client = None
        if enable_cloud_logging and cloud_logging:
            try:
                self.cloud_client = cloud_logging.Client()
                self.cloud_client.setup_logging()
            except Exception as e:
                self.logger.warning(f"Could not setup cloud logging: {e}")
    
    def _sanitize_log_data(self, data: Any) -> Any:
        """Sanitize data before logging to remove potential PHI.
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        if isinstance(data, dict):
            # Remove common PHI fields
            phi_fields = [
                'ssn', 'social_security', 'patient_id', 'mrn', 
                'date_of_birth', 'dob', 'phone', 'email',
                'address', 'credit_card', 'policy_number'
            ]
            sanitized = {
                k: '[REDACTED]' if k.lower() in phi_fields else v
                for k, v in data.items()
            }
            return sanitized
        return data
    
    def info(self, message: str, extra: Optional[Dict] = None):
        """Log info message."""
        sanitized_extra = self._sanitize_log_data(extra) if extra else None
        if sanitized_extra:
            self.logger.info(f"{message} - {json.dumps(sanitized_extra)}")
        else:
            self.logger.info(message)
    
    def error(self, message: str, extra: Optional[Dict] = None, exc_info: bool = False):
        """Log error message."""
        sanitized_extra = self._sanitize_log_data(extra) if extra else None
        if sanitized_extra:
            self.logger.error(f"{message} - {json.dumps(sanitized_extra)}", exc_info=exc_info)
        else:
            self.logger.error(message, exc_info=exc_info)
    
    def warning(self, message: str, extra: Optional[Dict] = None):
        """Log warning message."""
        sanitized_extra = self._sanitize_log_data(extra) if extra else None
        if sanitized_extra:
            self.logger.warning(f"{message} - {json.dumps(sanitized_extra)}")
        else:
            self.logger.warning(message)
    
    def debug(self, message: str, extra: Optional[Dict] = None):
        """Log debug message."""
        sanitized_extra = self._sanitize_log_data(extra) if extra else None
        if sanitized_extra:
            self.logger.debug(f"{message} - {json.dumps(sanitized_extra)}")
        else:
            self.logger.debug(message)
    
    def audit(self, event_type: str, user_id: str, details: Dict):
        """Log audit event for compliance.
        
        Args:
            event_type: Type of event (e.g., 'access', 'modification', 'query')
            user_id: User or system performing action
            details: Event details (will be sanitized)
        """
        audit_entry = {
            'timestamp': utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': self._sanitize_log_data(details)
        }
        self.logger.info(f"AUDIT: {json.dumps(audit_entry)}")


def get_logger(name: str, enable_cloud_logging: bool = False) -> HIPAACompliantLogger:
    """Get a HIPAA-compliant logger instance.
    
    Args:
        name: Logger name
        enable_cloud_logging: If True, also logs to Google Cloud Logging
        
    Returns:
        HIPAACompliantLogger instance
    """
    return HIPAACompliantLogger(name, enable_cloud_logging)
