"""Tests for PHI redaction utility."""

import pytest
from src.utils.phi_redaction import PHIRedactor


def test_ssn_redaction():
    """Test SSN redaction."""
    redactor = PHIRedactor()
    
    text = "My SSN is 123-45-6789"
    redacted, counts = redactor.redact(text)
    
    assert "[REDACTED_SSN]" in redacted
    assert "123-45-6789" not in redacted
    assert counts["ssn"] == 1


def test_phone_redaction():
    """Test phone number redaction."""
    redactor = PHIRedactor()
    
    text = "Call me at 555-123-4567"
    redacted, counts = redactor.redact(text)
    
    assert "[REDACTED_PHONE]" in redacted
    assert "555-123-4567" not in redacted
    assert counts["phone"] == 1


def test_email_redaction():
    """Test email redaction."""
    redactor = PHIRedactor()
    
    text = "Email: patient@example.com"
    redacted, counts = redactor.redact(text)
    
    assert "[REDACTED_EMAIL]" in redacted
    assert "patient@example.com" not in redacted
    assert counts["email"] == 1


def test_multiple_phi_types():
    """Test multiple PHI types in one text."""
    redactor = PHIRedactor()
    
    text = "Patient ID: 123456, SSN: 123-45-6789, call 555-1234"
    redacted, counts = redactor.redact(text)
    
    assert len(counts) >= 2
    assert "123-45-6789" not in redacted


def test_no_phi():
    """Test text with no PHI."""
    redactor = PHIRedactor()
    
    text = "I need to schedule an appointment"
    redacted, counts = redactor.redact(text)
    
    assert redacted == text
    assert len(counts) == 0


def test_is_text_safe():
    """Test safe text detection."""
    redactor = PHIRedactor()
    
    assert redactor.is_text_safe("I need help")
    assert not redactor.is_text_safe("My SSN is 123-45-6789")


def test_redact_dict():
    """Test dictionary redaction."""
    redactor = PHIRedactor()
    
    data = {
        "message": "Call me at 555-1234",
        "patient_info": "SSN: 123-45-6789"
    }
    
    redacted = redactor.redact_dict(data)
    
    assert "[REDACTED" in redacted["message"]
    assert "[REDACTED" in redacted["patient_info"]
