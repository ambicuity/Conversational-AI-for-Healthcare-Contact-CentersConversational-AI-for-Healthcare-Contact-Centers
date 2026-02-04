"""CRM abstraction layer for healthcare contact center."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from src.utils.logging import get_logger
from src.utils import utcnow

logger = get_logger(__name__)


class CRMProvider(ABC):
    """Abstract base class for CRM providers."""
    
    @abstractmethod
    def get_patient_info(self, patient_id: str) -> Dict[str, Any]:
        """Get patient information.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Patient information
        """
        pass
    
    @abstractmethod
    def get_patient_history(
        self,
        patient_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get patient interaction history.
        
        Args:
            patient_id: Patient identifier
            limit: Maximum records to return
            
        Returns:
            List of historical interactions
        """
        pass
    
    @abstractmethod
    def create_case(
        self,
        patient_id: str,
        subject: str,
        description: str,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """Create a new case/ticket.
        
        Args:
            patient_id: Patient identifier
            subject: Case subject
            description: Case description
            priority: Priority level
            
        Returns:
            Created case information
        """
        pass
    
    @abstractmethod
    def update_case(
        self,
        case_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing case.
        
        Args:
            case_id: Case identifier
            updates: Fields to update
            
        Returns:
            Updated case information
        """
        pass
    
    @abstractmethod
    def log_conversation(
        self,
        patient_id: str,
        conversation_summary: str,
        conversation_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Log conversation summary to CRM.
        
        Args:
            patient_id: Patient identifier
            conversation_summary: Summary text
            conversation_id: Conversation identifier
            metadata: Additional metadata
            
        Returns:
            Logged record information
        """
        pass
    
    @abstractmethod
    def get_appointments(
        self,
        patient_id: str,
        include_past: bool = False
    ) -> List[Dict[str, Any]]:
        """Get patient appointments.
        
        Args:
            patient_id: Patient identifier
            include_past: Include past appointments
            
        Returns:
            List of appointments
        """
        pass
    
    @abstractmethod
    def schedule_appointment(
        self,
        patient_id: str,
        appointment_type: str,
        datetime_str: str,
        provider_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Schedule new appointment.
        
        Args:
            patient_id: Patient identifier
            appointment_type: Type of appointment
            datetime_str: Appointment date/time
            provider_id: Provider identifier
            notes: Additional notes
            
        Returns:
            Appointment information
        """
        pass
    
    @abstractmethod
    def get_insurance_info(self, patient_id: str) -> Dict[str, Any]:
        """Get patient insurance information.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Insurance information
        """
        pass


class SalesforceCRM(CRMProvider):
    """Salesforce CRM implementation."""
    
    def __init__(self, api_endpoint: str, api_key: str):
        """Initialize Salesforce CRM client.
        
        Args:
            api_endpoint: Salesforce API endpoint
            api_key: API authentication key
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        logger.info("Salesforce CRM client initialized")
    
    def get_patient_info(self, patient_id: str) -> Dict[str, Any]:
        """Get patient information from Salesforce."""
        # In production, this would make actual Salesforce API calls
        logger.info(f"Fetching patient info for {patient_id}")
        
        # Mock response
        return {
            "patient_id": patient_id,
            "name": "John Doe",
            "email": "[REDACTED_EMAIL]",
            "phone": "[REDACTED_PHONE]",
            "date_of_birth": "[REDACTED_DATE]",
            "insurance_provider": "BlueCross BlueShield",
            "primary_care_physician": "Dr. Sarah Johnson"
        }
    
    def get_patient_history(
        self,
        patient_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get patient interaction history."""
        logger.info(f"Fetching patient history for {patient_id}")
        
        # Mock response
        return [
            {
                "id": "hist_001",
                "date": "2024-01-15",
                "type": "appointment",
                "summary": "Annual checkup - completed",
                "provider": "Dr. Sarah Johnson"
            },
            {
                "id": "hist_002",
                "date": "2024-01-10",
                "type": "call",
                "summary": "Insurance coverage inquiry",
                "agent": "Agent Smith"
            }
        ]
    
    def create_case(
        self,
        patient_id: str,
        subject: str,
        description: str,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """Create case in Salesforce."""
        logger.info(f"Creating case for patient {patient_id}: {subject}")
        
        case_id = f"case_{patient_id}_{utcnow().timestamp()}"
        
        return {
            "case_id": case_id,
            "patient_id": patient_id,
            "subject": subject,
            "description": description,
            "priority": priority,
            "status": "new",
            "created_at": utcnow().isoformat()
        }
    
    def update_case(
        self,
        case_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update case in Salesforce."""
        logger.info(f"Updating case {case_id}")
        
        return {
            "case_id": case_id,
            "updated_fields": list(updates.keys()),
            "updated_at": utcnow().isoformat()
        }
    
    def log_conversation(
        self,
        patient_id: str,
        conversation_summary: str,
        conversation_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Log conversation to Salesforce."""
        logger.info(f"Logging conversation {conversation_id} for patient {patient_id}")
        
        return {
            "log_id": f"log_{conversation_id}",
            "patient_id": patient_id,
            "conversation_id": conversation_id,
            "summary": conversation_summary,
            "metadata": metadata or {},
            "logged_at": utcnow().isoformat()
        }
    
    def get_appointments(
        self,
        patient_id: str,
        include_past: bool = False
    ) -> List[Dict[str, Any]]:
        """Get patient appointments."""
        logger.info(f"Fetching appointments for patient {patient_id}")
        
        # Mock response
        return [
            {
                "appointment_id": "appt_001",
                "patient_id": patient_id,
                "type": "follow-up",
                "datetime": "2024-02-20T10:00:00Z",
                "provider": "Dr. Sarah Johnson",
                "status": "scheduled"
            }
        ]
    
    def schedule_appointment(
        self,
        patient_id: str,
        appointment_type: str,
        datetime_str: str,
        provider_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Schedule appointment in Salesforce."""
        logger.info(f"Scheduling {appointment_type} for patient {patient_id}")
        
        appointment_id = f"appt_{patient_id}_{utcnow().timestamp()}"
        
        return {
            "appointment_id": appointment_id,
            "patient_id": patient_id,
            "type": appointment_type,
            "datetime": datetime_str,
            "provider_id": provider_id,
            "notes": notes,
            "status": "scheduled",
            "created_at": utcnow().isoformat()
        }
    
    def get_insurance_info(self, patient_id: str) -> Dict[str, Any]:
        """Get insurance information."""
        logger.info(f"Fetching insurance info for patient {patient_id}")
        
        # Mock response
        return {
            "patient_id": patient_id,
            "provider": "BlueCross BlueShield",
            "policy_number": "[REDACTED_POLICY]",
            "group_number": "[REDACTED]",
            "coverage_type": "PPO",
            "copay": "$25",
            "deductible": "$1,500",
            "deductible_met": "$500",
            "active": True
        }


class CRMFactory:
    """Factory for creating CRM provider instances."""
    
    @staticmethod
    def create_crm(
        provider: str,
        api_endpoint: str,
        api_key: str
    ) -> CRMProvider:
        """Create CRM provider instance.
        
        Args:
            provider: Provider name (e.g., 'salesforce')
            api_endpoint: API endpoint
            api_key: API key
            
        Returns:
            CRM provider instance
        """
        if provider.lower() == "salesforce":
            return SalesforceCRM(api_endpoint, api_key)
        else:
            raise ValueError(f"Unsupported CRM provider: {provider}")
