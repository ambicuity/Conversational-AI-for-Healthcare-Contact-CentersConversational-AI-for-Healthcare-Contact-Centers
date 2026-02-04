"""Utilities package for Healthcare Conversational AI Platform."""

from datetime import datetime, timezone

from .phi_redaction import PHIRedactor, phi_redactor
from .logging import HIPAACompliantLogger, get_logger


def utcnow() -> datetime:
    """Get current UTC datetime in a Python 3.12+ compatible way.
    
    Returns:
        Current UTC datetime with timezone awareness
    """
    try:
        # Python 3.12+ preferred method
        return datetime.now(timezone.utc)
    except AttributeError:
        # Fallback for older Python versions
        return datetime.utcnow().replace(tzinfo=timezone.utc)


__all__ = [
    'PHIRedactor',
    'phi_redactor',
    'HIPAACompliantLogger',
    'get_logger',
    'utcnow',
]
