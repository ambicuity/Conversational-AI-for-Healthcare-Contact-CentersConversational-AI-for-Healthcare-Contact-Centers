"""Google Gemini LLM service for conversation AI capabilities."""

import google.generativeai as genai
from typing import Dict, List, Any, Optional
import json

from config.config import config
from src.utils.logging import get_logger
from src.utils.phi_redaction import phi_redactor

logger = get_logger(__name__)


class GeminiService:
    """Service for Google Gemini LLM interactions."""
    
    # Prompt templates optimized for healthcare
    SUMMARIZATION_PROMPT = """
You are a medical assistant helping to summarize patient conversations.
Create a concise, professional summary of the following conversation that captures:
- Main reason for contact
- Key information provided by patient
- Actions taken or promised
- Any follow-up needed

Conversation:
{conversation}

Provide a summary in 3-5 bullet points.
"""
    
    SMART_REPLY_PROMPT = """
You are an AI assistant helping a healthcare contact center agent respond to a patient.
Based on the conversation context below, suggest 3 appropriate next responses.

Conversation Context:
{context}

Patient's Last Message: {last_message}

Generate 3 response suggestions that are:
- Professional and empathetic
- Compliant with healthcare communication standards
- Actionable and helpful
- Brief (1-2 sentences each)

Format as JSON array of strings.
"""
    
    INTENT_CLARIFICATION_PROMPT = """
You are helping to clarify patient intent in a healthcare conversation.

Patient said: "{message}"

Current detected intent: {intent}
Confidence: {confidence}

Is this intent classification correct? If uncertain, what clarifying question should be asked?
Provide your response in JSON format:
{{
    "is_correct": true/false,
    "confidence_assessment": "high/medium/low",
    "clarifying_question": "question text or null"
}}
"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = None):
        """Initialize Gemini service.
        
        Args:
            api_key: Google API key (if not using default credentials)
            model_name: Model name to use
        """
        self.model_name = model_name or config.gcp.gemini_model
        
        # Configure API
        if api_key:
            genai.configure(api_key=api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(self.model_name)
        
        # Safety settings for healthcare context
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        logger.info(f"Gemini service initialized with model: {self.model_name}")
    
    def _redact_phi_from_conversation(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Redact PHI from conversation messages before sending to LLM.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Messages with PHI redacted
        """
        redacted_messages = []
        for msg in messages:
            redacted_text, _ = phi_redactor.redact(msg.get("text", ""))
            redacted_messages.append({
                "role": msg.get("role", "user"),
                "text": redacted_text
            })
        return redacted_messages
    
    def summarize_conversation(
        self,
        messages: List[Dict[str, str]],
        redact_phi: bool = True
    ) -> Dict[str, Any]:
        """Generate conversation summary.
        
        Args:
            messages: List of conversation messages with 'role' and 'text'
            redact_phi: Whether to redact PHI before sending to LLM
            
        Returns:
            Dict with summary and metadata
        """
        try:
            # Redact PHI if enabled
            if redact_phi:
                messages = self._redact_phi_from_conversation(messages)
            
            # Format conversation
            conversation_text = "\n".join([
                f"{msg['role'].upper()}: {msg['text']}"
                for msg in messages
            ])
            
            # Generate prompt
            prompt = self.SUMMARIZATION_PROMPT.format(conversation=conversation_text)
            
            # Generate summary
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            
            summary = response.text.strip()
            
            logger.info("Conversation summarized", {
                "message_count": len(messages),
                "summary_length": len(summary)
            })
            
            return {
                "summary": summary,
                "message_count": len(messages),
                "model": self.model_name,
            }
        
        except Exception as e:
            logger.error(f"Error summarizing conversation: {e}", exc_info=True)
            raise
    
    def generate_smart_replies(
        self,
        context_messages: List[Dict[str, str]],
        last_message: str,
        redact_phi: bool = True,
        num_replies: int = 3
    ) -> Dict[str, Any]:
        """Generate smart reply suggestions.
        
        Args:
            context_messages: Previous conversation messages
            last_message: Patient's most recent message
            redact_phi: Whether to redact PHI
            num_replies: Number of reply suggestions to generate
            
        Returns:
            Dict with reply suggestions and confidence scores
        """
        try:
            # Redact PHI
            if redact_phi:
                context_messages = self._redact_phi_from_conversation(context_messages)
                last_message, _ = phi_redactor.redact(last_message)
            
            # Format context
            context_text = "\n".join([
                f"{msg['role'].upper()}: {msg['text']}"
                for msg in context_messages[-5:]  # Last 5 messages for context
            ])
            
            # Generate prompt
            prompt = self.SMART_REPLY_PROMPT.format(
                context=context_text,
                last_message=last_message
            )
            
            # Generate replies
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            
            # Parse response (expecting JSON array)
            try:
                replies = json.loads(response.text.strip())
                if not isinstance(replies, list):
                    replies = [response.text.strip()]
            except json.JSONDecodeError:
                # Fallback: split by newlines and remove list markers
                replies = []
                for line in response.text.strip().split('\n'):
                    if line.strip():
                        # Remove common list prefixes (1., 2., -, *)
                        cleaned = line.strip()
                        if cleaned and len(cleaned) > 2:
                            # Remove numbered list markers like "1. ", "2. "
                            if cleaned[0].isdigit() and cleaned[1] in '.):':
                                cleaned = cleaned[2:].strip()
                            # Remove bullet points
                            elif cleaned[0] in '-*•':
                                cleaned = cleaned[1:].strip()
                        if cleaned:
                            replies.append(cleaned)
                replies = replies[:num_replies]
            
            # Calculate confidence scores (placeholder - in production, use more sophisticated scoring)
            confidence_scores = [0.85, 0.80, 0.75][:len(replies)]
            
            result = {
                "replies": [
                    {
                        "text": reply,
                        "confidence": confidence_scores[i] if i < len(confidence_scores) else 0.7
                    }
                    for i, reply in enumerate(replies[:num_replies])
                ],
                "model": self.model_name,
            }
            
            logger.info("Smart replies generated", {
                "num_replies": len(result["replies"])
            })
            
            return result
        
        except Exception as e:
            logger.error(f"Error generating smart replies: {e}", exc_info=True)
            raise
    
    def clarify_intent(
        self,
        message: str,
        detected_intent: str,
        confidence: float,
        redact_phi: bool = True
    ) -> Dict[str, Any]:
        """Clarify or reinforce intent detection.
        
        Args:
            message: User's message
            detected_intent: Intent detected by Dialogflow
            confidence: Confidence score
            redact_phi: Whether to redact PHI
            
        Returns:
            Dict with clarification assessment
        """
        try:
            # Redact PHI
            if redact_phi:
                message, _ = phi_redactor.redact(message)
            
            # Generate prompt
            prompt = self.INTENT_CLARIFICATION_PROMPT.format(
                message=message,
                intent=detected_intent,
                confidence=confidence
            )
            
            # Generate assessment
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            
            # Parse JSON response
            try:
                assessment = json.loads(response.text.strip())
            except json.JSONDecodeError:
                # Fallback
                assessment = {
                    "is_correct": confidence > 0.7,
                    "confidence_assessment": "medium",
                    "clarifying_question": None
                }
            
            logger.info("Intent clarified", {
                "original_intent": detected_intent,
                "is_correct": assessment.get("is_correct")
            })
            
            return assessment
        
        except Exception as e:
            logger.error(f"Error clarifying intent: {e}", exc_info=True)
            raise
    
    def generate_knowledge_snippet(
        self,
        query: str,
        knowledge_base: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate knowledge base snippet relevant to query.
        
        Args:
            query: Agent's query or patient question
            knowledge_base: Optional list of knowledge articles
            
        Returns:
            Relevant knowledge snippet
        """
        try:
            prompt = f"""
Based on the following query from a healthcare contact center agent,
provide a brief, actionable knowledge snippet (2-3 sentences) that would help them respond.

Query: {query}

Provide practical, compliant information.
"""
            
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            
            return {
                "snippet": response.text.strip(),
                "relevance_score": 0.85,  # Placeholder
                "model": self.model_name
            }
        
        except Exception as e:
            logger.error(f"Error generating knowledge snippet: {e}", exc_info=True)
            raise


# Singleton instance
gemini_service = GeminiService()
