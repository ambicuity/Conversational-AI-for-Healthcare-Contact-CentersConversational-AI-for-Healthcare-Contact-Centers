"""Genesys webhook handlers."""

from typing import Dict, Any
from flask import Request
import hashlib
import hmac

from config.config import config
from src.utils.logging import get_logger
from src.agent_assist.service import agent_assist_service

logger = get_logger(__name__)


class GenesysWebhookHandler:
    """Handler for Genesys Cloud webhooks."""
    
    # Event types
    EVENT_CONVERSATION_START = "v2.conversations.start"
    EVENT_MESSAGE_RECEIVED = "v2.conversations.messages.created"
    EVENT_AGENT_JOINED = "v2.conversations.participants.agent.joined"
    EVENT_CONVERSATION_END = "v2.conversations.end"
    
    def __init__(self, webhook_secret: str = None):
        """Initialize webhook handler.
        
        Args:
            webhook_secret: Webhook validation secret
        """
        self.webhook_secret = webhook_secret or config.genesys.webhook_secret
        logger.info("Genesys webhook handler initialized")
    
    def validate_signature(self, request: Request) -> bool:
        """Validate webhook signature.
        
        Args:
            request: Flask request object
            
        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured, skipping validation")
            return True
        
        try:
            signature = request.headers.get("X-Genesys-Signature")
            if not signature:
                return False
            
            # Calculate expected signature
            body = request.get_data()
            expected = hmac.new(
                self.webhook_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected)
        
        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}", exc_info=True)
            return False
    
    def handle_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Route webhook event to appropriate handler.
        
        Args:
            event_type: Genesys event type
            payload: Event payload
            
        Returns:
            Handler response
        """
        handlers = {
            self.EVENT_CONVERSATION_START: self._handle_conversation_start,
            self.EVENT_MESSAGE_RECEIVED: self._handle_message_received,
            self.EVENT_AGENT_JOINED: self._handle_agent_joined,
            self.EVENT_CONVERSATION_END: self._handle_conversation_end,
        }
        
        handler = handlers.get(event_type)
        
        if handler:
            logger.info(f"Handling webhook event: {event_type}")
            return handler(payload)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            return {"status": "ignored", "event_type": event_type}
    
    def _handle_conversation_start(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle conversation start event.
        
        Args:
            payload: Event payload
            
        Returns:
            Response
        """
        conversation_id = payload.get("id")
        
        if conversation_id:
            # Register conversation with Agent Assist
            agent_assist_service.register_conversation(conversation_id)
            
            logger.info(f"Conversation started: {conversation_id}")
            
            return {
                "status": "processed",
                "conversation_id": conversation_id,
                "action": "registered"
            }
        
        return {"status": "error", "message": "No conversation ID"}
    
    def _handle_message_received(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle message received event.
        
        Args:
            payload: Event payload
            
        Returns:
            Response
        """
        conversation_id = payload.get("conversationId")
        message = payload.get("message", {})
        
        if not conversation_id or not message:
            return {"status": "error", "message": "Invalid payload"}
        
        # Extract message details
        sender_type = message.get("type", "unknown")  # "agent" or "customer"
        text = message.get("text", "")
        timestamp = message.get("timestamp")
        
        # Map to our role system
        role = "agent" if sender_type == "agent" else "patient"
        
        # Add message to conversation
        agent_assist_service.add_message(
            conversation_id,
            role,
            text,
            timestamp
        )
        
        logger.info(f"Message added to conversation {conversation_id}")
        
        # Trigger Agent Assist if it's a patient message
        if role == "patient":
            # In production, this would trigger async processing
            # to generate real-time assistance
            logger.info(f"Triggering Agent Assist for conversation {conversation_id}")
        
        return {
            "status": "processed",
            "conversation_id": conversation_id,
            "message_role": role
        }
    
    def _handle_agent_joined(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent joined event (handoff from bot).
        
        Args:
            payload: Event payload
            
        Returns:
            Response
        """
        conversation_id = payload.get("conversationId")
        participant = payload.get("participant", {})
        
        agent_id = participant.get("userId")
        agent_name = participant.get("name", "Agent")
        
        logger.info(
            f"Agent {agent_name} ({agent_id}) joined conversation {conversation_id}"
        )
        
        # Add system message
        agent_assist_service.add_message(
            conversation_id,
            "system",
            f"Agent {agent_name} joined the conversation"
        )
        
        return {
            "status": "processed",
            "conversation_id": conversation_id,
            "agent_id": agent_id,
            "action": "agent_joined"
        }
    
    def _handle_conversation_end(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle conversation end event.
        
        Args:
            payload: Event payload
            
        Returns:
            Response
        """
        conversation_id = payload.get("id")
        
        if conversation_id:
            # Close conversation in Agent Assist
            agent_assist_service.close_conversation(conversation_id)
            
            logger.info(f"Conversation ended: {conversation_id}")
            
            return {
                "status": "processed",
                "conversation_id": conversation_id,
                "action": "closed"
            }
        
        return {"status": "error", "message": "No conversation ID"}


# Event schemas for documentation
GENESYS_EVENT_SCHEMAS = {
    "conversation_start": {
        "id": "string",
        "participants": [
            {
                "id": "string",
                "purpose": "string",
                "state": "string"
            }
        ],
        "startTime": "datetime"
    },
    "message_received": {
        "conversationId": "string",
        "message": {
            "id": "string",
            "type": "string",  # "agent" or "customer"
            "text": "string",
            "timestamp": "datetime"
        }
    },
    "agent_joined": {
        "conversationId": "string",
        "participant": {
            "id": "string",
            "userId": "string",
            "name": "string",
            "purpose": "string"
        }
    },
    "conversation_end": {
        "id": "string",
        "endTime": "datetime",
        "participants": []
    }
}


# Singleton instance
webhook_handler = GenesysWebhookHandler()
