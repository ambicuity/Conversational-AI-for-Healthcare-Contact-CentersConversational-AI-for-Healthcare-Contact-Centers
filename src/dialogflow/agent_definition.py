"""
Dialogflow CX Agent Definition for Healthcare Contact Center

This module defines the conversational flows, intents, and entities
for handling patient inquiries in a healthcare contact center.

Flow Architecture:
==================
Start → Default Welcome → Intent Router → Specialized Flows
                                        ├→ Appointment Scheduling
                                        ├→ Insurance & Billing
                                        ├→ Prescription Refills
                                        ├→ Lab Results
                                        └→ Provider Availability

Each flow includes:
- Intent matching
- Entity extraction
- Multi-turn conversations
- Context management
- Fallback handling
- Agent handoff triggers
"""

from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class TrainingPhrase:
    """Training phrase for intent."""
    text: str
    parts: List[Dict[str, str]] = None


@dataclass
class Intent:
    """Dialogflow CX Intent definition."""
    display_name: str
    training_phrases: List[TrainingPhrase]
    priority: int = 500000
    description: str = ""


@dataclass
class Entity:
    """Dialogflow CX Entity definition."""
    display_name: str
    kind: str  # KIND_MAP or KIND_LIST
    entities: List[Dict[str, Any]]
    enable_fuzzy_extraction: bool = True


# ============================================================================
# ENTITY DEFINITIONS
# ============================================================================

ENTITIES = {
    "appointment_type": Entity(
        display_name="AppointmentType",
        kind="KIND_LIST",
        entities=[
            {"value": "checkup", "synonyms": ["check-up", "physical", "wellness visit"]},
            {"value": "consultation", "synonyms": ["consult", "initial visit", "new patient"]},
            {"value": "follow-up", "synonyms": ["followup", "follow up", "return visit"]},
            {"value": "urgent", "synonyms": ["urgent care", "same-day", "emergency"]},
            {"value": "lab_work", "synonyms": ["blood test", "lab test", "diagnostic"]},
            {"value": "imaging", "synonyms": ["x-ray", "MRI", "CT scan", "ultrasound"]},
        ]
    ),
    
    "department": Entity(
        display_name="Department",
        kind="KIND_LIST",
        entities=[
            {"value": "cardiology", "synonyms": ["heart", "cardiac"]},
            {"value": "dermatology", "synonyms": ["skin", "dermatologist"]},
            {"value": "orthopedics", "synonyms": ["bone", "joint", "orthopedic"]},
            {"value": "primary_care", "synonyms": ["family medicine", "general practice", "PCP"]},
            {"value": "pediatrics", "synonyms": ["children", "kids", "pediatrician"]},
            {"value": "neurology", "synonyms": ["brain", "neurologist", "nerve"]},
        ]
    ),
    
    "insurance_topic": Entity(
        display_name="InsuranceTopic",
        kind="KIND_LIST",
        entities=[
            {"value": "coverage", "synonyms": ["covered", "covers", "insurance coverage"]},
            {"value": "copay", "synonyms": ["co-pay", "copayment", "out of pocket"]},
            {"value": "deductible", "synonyms": ["deductible amount"]},
            {"value": "claim", "synonyms": ["insurance claim", "claim status"]},
            {"value": "billing", "synonyms": ["bill", "invoice", "statement"]},
            {"value": "prior_auth", "synonyms": ["prior authorization", "pre-approval"]},
        ]
    ),
}


# ============================================================================
# INTENT DEFINITIONS
# ============================================================================

INTENTS = {
    # Appointment Scheduling Intents
    "schedule_appointment": Intent(
        display_name="appointment.schedule",
        description="Patient wants to schedule a new appointment",
        training_phrases=[
            TrainingPhrase("I need to schedule an appointment"),
            TrainingPhrase("Can I book an appointment?"),
            TrainingPhrase("I want to see a doctor"),
            TrainingPhrase("Schedule a checkup for me"),
            TrainingPhrase("I'd like to make an appointment"),
            TrainingPhrase("Book me for a consultation"),
            TrainingPhrase("I need to see a cardiologist"),
            TrainingPhrase("Can I get an appointment for next week?"),
            TrainingPhrase("I want to schedule a physical"),
            TrainingPhrase("Set up an appointment with Dr. Smith"),
        ]
    ),
    
    "reschedule_appointment": Intent(
        display_name="appointment.reschedule",
        description="Patient wants to change existing appointment",
        training_phrases=[
            TrainingPhrase("I need to reschedule my appointment"),
            TrainingPhrase("Can I change my appointment time?"),
            TrainingPhrase("I can't make my appointment tomorrow"),
            TrainingPhrase("Move my appointment to another day"),
            TrainingPhrase("Reschedule my visit"),
            TrainingPhrase("I need a different time slot"),
        ]
    ),
    
    "cancel_appointment": Intent(
        display_name="appointment.cancel",
        description="Patient wants to cancel appointment",
        training_phrases=[
            TrainingPhrase("I need to cancel my appointment"),
            TrainingPhrase("Cancel my scheduled visit"),
            TrainingPhrase("I can't make it to my appointment"),
            TrainingPhrase("Please cancel my booking"),
        ]
    ),
    
    # Insurance & Billing Intents
    "insurance_coverage": Intent(
        display_name="insurance.coverage",
        description="Questions about insurance coverage",
        training_phrases=[
            TrainingPhrase("Is this covered by my insurance?"),
            TrainingPhrase("Does my insurance cover this procedure?"),
            TrainingPhrase("What does my insurance pay for?"),
            TrainingPhrase("Check my insurance coverage"),
            TrainingPhrase("Will insurance pay for this?"),
            TrainingPhrase("Is my insurance accepted?"),
        ]
    ),
    
    "billing_inquiry": Intent(
        display_name="billing.inquiry",
        description="Questions about medical bills",
        training_phrases=[
            TrainingPhrase("I have a question about my bill"),
            TrainingPhrase("Why was I charged this amount?"),
            TrainingPhrase("I received a billing statement"),
            TrainingPhrase("What is this charge for?"),
            TrainingPhrase("Explain my medical bill"),
            TrainingPhrase("I don't understand this invoice"),
        ]
    ),
    
    # Prescription Intents
    "prescription_refill": Intent(
        display_name="prescription.refill",
        description="Request prescription refill",
        training_phrases=[
            TrainingPhrase("I need a prescription refill"),
            TrainingPhrase("Refill my medication"),
            TrainingPhrase("My prescription is running out"),
            TrainingPhrase("Can you refill my prescription?"),
            TrainingPhrase("I need more of my medication"),
            TrainingPhrase("Request refill for my medicine"),
        ]
    ),
    
    "prescription_status": Intent(
        display_name="prescription.status",
        description="Check prescription status",
        training_phrases=[
            TrainingPhrase("Is my prescription ready?"),
            TrainingPhrase("Check prescription status"),
            TrainingPhrase("When will my medication be ready?"),
            TrainingPhrase("Has my prescription been filled?"),
        ]
    ),
    
    # Lab Results Intents
    "lab_results": Intent(
        display_name="lab.results",
        description="Inquire about lab results",
        training_phrases=[
            TrainingPhrase("Are my lab results ready?"),
            TrainingPhrase("I want to check my test results"),
            TrainingPhrase("Did my blood work come back?"),
            TrainingPhrase("Can I get my lab results?"),
            TrainingPhrase("Check the status of my lab tests"),
        ]
    ),
    
    # Provider Availability
    "provider_availability": Intent(
        display_name="provider.availability",
        description="Check provider availability",
        training_phrases=[
            TrainingPhrase("Is Dr. Johnson available?"),
            TrainingPhrase("When can I see Dr. Smith?"),
            TrainingPhrase("What's the doctor's schedule?"),
            TrainingPhrase("Does the doctor have any openings?"),
            TrainingPhrase("Check provider availability"),
        ]
    ),
    
    # Agent Handoff Intent
    "speak_to_agent": Intent(
        display_name="agent.handoff",
        description="Patient requests to speak to live agent",
        priority=600000,  # Higher priority
        training_phrases=[
            TrainingPhrase("I want to speak to a person"),
            TrainingPhrase("Connect me to an agent"),
            TrainingPhrase("I need human help"),
            TrainingPhrase("Transfer me to someone"),
            TrainingPhrase("Let me talk to a representative"),
            TrainingPhrase("This isn't helping, get me an agent"),
        ]
    ),
}


# ============================================================================
# CONVERSATION FLOWS
# ============================================================================

FLOWS = {
    "appointment_scheduling": {
        "display_name": "Appointment Scheduling Flow",
        "description": "Handles appointment booking, rescheduling, and cancellation",
        "pages": [
            {
                "name": "collect_appointment_type",
                "entry_fulfillment": {
                    "messages": [{
                        "text": "I can help you with your appointment. What type of appointment do you need?"
                    }]
                },
                "form": {
                    "parameters": [
                        {
                            "display_name": "appointment_type",
                            "entity_type": "AppointmentType",
                            "required": True,
                            "prompts": ["What kind of appointment? (checkup, consultation, follow-up, urgent care)"]
                        }
                    ]
                },
                "transition_routes": [
                    {"intent": "speak_to_agent", "target_page": "agent_handoff"}
                ]
            },
            {
                "name": "collect_date_time",
                "entry_fulfillment": {
                    "messages": [{
                        "text": "When would you like to schedule your appointment?"
                    }]
                },
                "form": {
                    "parameters": [
                        {
                            "display_name": "date",
                            "entity_type": "@sys.date",
                            "required": True,
                            "prompts": ["What date works for you?"]
                        },
                        {
                            "display_name": "time",
                            "entity_type": "@sys.time",
                            "required": True,
                            "prompts": ["What time would you prefer? (morning, afternoon, evening)"]
                        }
                    ]
                }
            },
            {
                "name": "confirm_appointment",
                "entry_fulfillment": {
                    "webhook": "webhook_appointment_confirm",
                    "messages": [{
                        "text": "Let me check availability and confirm your appointment."
                    }]
                }
            }
        ]
    },
    
    "insurance_billing": {
        "display_name": "Insurance & Billing Flow",
        "description": "Handles insurance coverage and billing inquiries",
        "pages": [
            {
                "name": "collect_insurance_info",
                "entry_fulfillment": {
                    "messages": [{
                        "text": "I can help with insurance questions. What would you like to know about?"
                    }]
                },
                "form": {
                    "parameters": [
                        {
                            "display_name": "insurance_topic",
                            "entity_type": "InsuranceTopic",
                            "required": True,
                        }
                    ]
                }
            },
            {
                "name": "lookup_insurance",
                "entry_fulfillment": {
                    "webhook": "webhook_insurance_lookup",
                    "messages": [{
                        "text": "Let me look up your insurance information."
                    }]
                }
            }
        ]
    },
    
    "prescription_management": {
        "display_name": "Prescription Management Flow",
        "description": "Handles prescription refills and status checks",
        "pages": [
            {
                "name": "collect_prescription_info",
                "entry_fulfillment": {
                    "messages": [{
                        "text": "I can help with your prescriptions. What medication do you need?"
                    }]
                },
                "form": {
                    "parameters": [
                        {
                            "display_name": "medication_name",
                            "entity_type": "@sys.any",
                            "required": True,
                            "prompts": ["What is the name of your medication?"]
                        }
                    ]
                }
            },
            {
                "name": "process_refill",
                "entry_fulfillment": {
                    "webhook": "webhook_prescription_refill",
                    "messages": [{
                        "text": "Processing your prescription refill request."
                    }]
                }
            }
        ]
    }
}


# ============================================================================
# WEBHOOK FULFILLMENT MAPPINGS
# ============================================================================

WEBHOOKS = {
    "webhook_appointment_confirm": {
        "url": "/webhooks/dialogflow/appointment",
        "method": "POST",
        "description": "Confirms appointment availability and books in CRM"
    },
    "webhook_insurance_lookup": {
        "url": "/webhooks/dialogflow/insurance",
        "method": "POST",
        "description": "Looks up insurance coverage in CRM"
    },
    "webhook_prescription_refill": {
        "url": "/webhooks/dialogflow/prescription",
        "method": "POST",
        "description": "Processes prescription refill request"
    },
}


def export_agent_definition(filepath: str):
    """Export complete agent definition to JSON file.
    
    Args:
        filepath: Path to save the JSON file
    """
    agent_def = {
        "displayName": "Healthcare Contact Center Agent",
        "defaultLanguageCode": "en",
        "timeZone": "America/New_York",
        "description": "Conversational AI agent for healthcare patient inquiries",
        "entities": {k: asdict(v) for k, v in ENTITIES.items()},
        "intents": {k: asdict(v) for k, v in INTENTS.items()},
        "flows": FLOWS,
        "webhooks": WEBHOOKS,
    }
    
    with open(filepath, 'w') as f:
        json.dump(agent_def, f, indent=2)


if __name__ == "__main__":
    # Export agent definition
    export_agent_definition("dialogflow_agent.json")
    print("Agent definition exported to dialogflow_agent.json")
