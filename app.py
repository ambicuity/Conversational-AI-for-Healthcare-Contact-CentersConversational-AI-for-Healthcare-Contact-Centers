"""Main Flask application for Healthcare Conversational AI Platform."""

from flask import Flask, request, jsonify
import asyncio
from typing import Dict, Any

from config.config import config
from src.utils.logging import get_logger
from src.dialogflow.client import DialogflowClient
from src.llm_services.gemini_service import gemini_service
from src.agent_assist.service import agent_assist_service
from src.genesys.webhooks import webhook_handler
from src.crm.provider import CRMFactory

logger = get_logger(__name__, enable_cloud_logging=True)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize services
dialogflow_client = DialogflowClient()
crm_client = CRMFactory.create_crm(
    provider=config.crm.provider,
    api_endpoint=config.crm.api_endpoint or "https://api.example.com",
    api_key=config.crm.api_key or "dummy-key"
)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "environment": config.environment,
        "services": {
            "dialogflow": "ready",
            "gemini": "ready",
            "agent_assist": "ready",
            "genesys": "ready",
            "crm": "ready"
        }
    })


@app.route('/api/v1/conversations/detect-intent', methods=['POST'])
def detect_intent():
    """Detect intent from user input via Dialogflow CX.
    
    Request body:
    {
        "session_id": "unique-session-id",
        "text": "I need to schedule an appointment",
        "language_code": "en"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data or 'text' not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        session_id = data['session_id']
        text = data['text']
        language_code = data.get('language_code', 'en')
        
        # Detect intent
        result = dialogflow_client.detect_intent(
            session_id=session_id,
            text=text,
            language_code=language_code
        )
        
        logger.audit("intent_detection", session_id, {
            "intent": result["intent"]["name"],
            "confidence": result["intent"]["confidence"]
        })
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error detecting intent: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/agent-assist', methods=['POST'])
def get_agent_assist():
    """Get real-time agent assistance.
    
    Request body:
    {
        "conversation_id": "conv-123",
        "include_summary": true,
        "include_smart_replies": true,
        "include_knowledge": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'conversation_id' not in data:
            return jsonify({"error": "Missing conversation_id"}), 400
        
        conversation_id = data['conversation_id']
        
        # Generate agent assist (async)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        assist_response = loop.run_until_complete(
            agent_assist_service.generate_real_time_assist(
                conversation_id=conversation_id,
                include_summary=data.get('include_summary', True),
                include_smart_replies=data.get('include_smart_replies', True),
                include_knowledge=data.get('include_knowledge', True)
            )
        )
        
        loop.close()
        
        logger.audit("agent_assist_requested", conversation_id, {
            "has_summary": assist_response.summary is not None,
            "num_replies": len(assist_response.smart_replies or [])
        })
        
        return jsonify(assist_response.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Error generating agent assist: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/conversations/<conversation_id>/messages', methods=['POST'])
def add_conversation_message(conversation_id: str):
    """Add message to conversation.
    
    Request body:
    {
        "role": "patient",
        "text": "I need help with my appointment"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'role' not in data or 'text' not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        agent_assist_service.add_message(
            conversation_id=conversation_id,
            role=data['role'],
            text=data['text']
        )
        
        return jsonify({"status": "success", "conversation_id": conversation_id}), 200
    
    except Exception as e:
        logger.error(f"Error adding message: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/webhooks/genesys', methods=['POST'])
def genesys_webhook():
    """Webhook endpoint for Genesys Cloud events."""
    try:
        # Validate signature
        if not webhook_handler.validate_signature(request):
            logger.warning("Invalid webhook signature")
            return jsonify({"error": "Invalid signature"}), 401
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Invalid payload"}), 400
        
        event_type = data.get('topicName') or data.get('eventType')
        
        # Handle webhook
        response = webhook_handler.handle_webhook(event_type, data)
        
        logger.audit("webhook_received", "genesys", {
            "event_type": event_type
        })
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error handling Genesys webhook: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/webhooks/dialogflow/appointment', methods=['POST'])
def dialogflow_webhook_appointment():
    """Dialogflow webhook for appointment scheduling."""
    try:
        data = request.get_json()
        
        session_info = data.get('sessionInfo', {})
        parameters = session_info.get('parameters', {})
        
        patient_id = parameters.get('patient_id')
        appointment_type = parameters.get('appointment_type')
        date = parameters.get('date')
        time = parameters.get('time')
        
        if not all([patient_id, appointment_type, date, time]):
            return jsonify({
                "fulfillmentResponse": {
                    "messages": [{
                        "text": {
                            "text": ["I need more information to schedule your appointment."]
                        }
                    }]
                }
            })
        
        # Schedule appointment in CRM
        datetime_str = f"{date}T{time}:00Z"
        appointment = crm_client.schedule_appointment(
            patient_id=patient_id,
            appointment_type=appointment_type,
            datetime_str=datetime_str
        )
        
        logger.audit("appointment_scheduled", patient_id, {
            "appointment_id": appointment['appointment_id'],
            "type": appointment_type
        })
        
        return jsonify({
            "fulfillmentResponse": {
                "messages": [{
                    "text": {
                        "text": [
                            f"Your {appointment_type} appointment has been scheduled "
                            f"for {date} at {time}. Your confirmation number is "
                            f"{appointment['appointment_id']}."
                        ]
                    }
                }]
            },
            "sessionInfo": {
                "parameters": {
                    "appointment_id": appointment['appointment_id']
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Error in appointment webhook: {e}", exc_info=True)
        return jsonify({
            "fulfillmentResponse": {
                "messages": [{
                    "text": {
                        "text": [
                            "I'm sorry, I encountered an error scheduling your appointment. "
                            "Let me connect you with an agent."
                        ]
                    }
                }]
            }
        }), 200


@app.route('/webhooks/dialogflow/insurance', methods=['POST'])
def dialogflow_webhook_insurance():
    """Dialogflow webhook for insurance inquiries."""
    try:
        data = request.get_json()
        
        session_info = data.get('sessionInfo', {})
        parameters = session_info.get('parameters', {})
        
        patient_id = parameters.get('patient_id')
        insurance_topic = parameters.get('insurance_topic')
        
        if not patient_id:
            return jsonify({
                "fulfillmentResponse": {
                    "messages": [{
                        "text": {
                            "text": ["I'll need to verify your identity first."]
                        }
                    }]
                }
            })
        
        # Get insurance info from CRM
        insurance_info = crm_client.get_insurance_info(patient_id)
        
        # Build response based on topic
        if insurance_topic == "coverage":
            response_text = (
                f"You have {insurance_info['coverage_type']} coverage with "
                f"{insurance_info['provider']}. Your plan is currently active."
            )
        elif insurance_topic == "copay":
            response_text = f"Your copay is {insurance_info['copay']} for most visits."
        elif insurance_topic == "deductible":
            response_text = (
                f"Your annual deductible is {insurance_info['deductible']}, "
                f"and you've met {insurance_info['deductible_met']} so far."
            )
        else:
            response_text = "I can help you with insurance questions. What would you like to know?"
        
        return jsonify({
            "fulfillmentResponse": {
                "messages": [{
                    "text": {
                        "text": [response_text]
                    }
                }]
            }
        })
    
    except Exception as e:
        logger.error(f"Error in insurance webhook: {e}", exc_info=True)
        return jsonify({
            "fulfillmentResponse": {
                "messages": [{
                    "text": {
                        "text": ["I'm having trouble accessing your insurance information."]
                    }
                }]
            }
        }), 200


@app.route('/webhooks/dialogflow/prescription', methods=['POST'])
def dialogflow_webhook_prescription():
    """Dialogflow webhook for prescription refills."""
    try:
        data = request.get_json()
        
        session_info = data.get('sessionInfo', {})
        parameters = session_info.get('parameters', {})
        
        patient_id = parameters.get('patient_id')
        medication_name = parameters.get('medication_name')
        
        if not all([patient_id, medication_name]):
            return jsonify({
                "fulfillmentResponse": {
                    "messages": [{
                        "text": {
                            "text": ["I need your patient ID and medication name."]
                        }
                    }]
                }
            })
        
        # Create case for prescription refill in CRM
        case = crm_client.create_case(
            patient_id=patient_id,
            subject=f"Prescription Refill: {medication_name}",
            description=f"Patient requested refill for {medication_name}",
            priority="normal"
        )
        
        logger.audit("prescription_refill_requested", patient_id, {
            "medication": medication_name,
            "case_id": case['case_id']
        })
        
        return jsonify({
            "fulfillmentResponse": {
                "messages": [{
                    "text": {
                        "text": [
                            f"I've submitted your refill request for {medication_name}. "
                            f"Your pharmacy should have it ready within 24 hours. "
                            f"Your reference number is {case['case_id']}."
                        ]
                    }
                }]
            }
        })
    
    except Exception as e:
        logger.error(f"Error in prescription webhook: {e}", exc_info=True)
        return jsonify({
            "fulfillmentResponse": {
                "messages": [{
                    "text": {
                        "text": ["I'm having trouble processing your prescription request."]
                    }
                }]
            }
        }), 200


@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    """Get platform metrics."""
    try:
        metrics = {
            "agent_assist": agent_assist_service.get_metrics(),
            "timestamp": "2024-02-04T18:30:00Z"
        }
        
        return jsonify(metrics), 200
    
    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    logger.info(f"Starting Healthcare Conversational AI Platform in {config.environment} mode")
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=config.environment == 'development'
    )
