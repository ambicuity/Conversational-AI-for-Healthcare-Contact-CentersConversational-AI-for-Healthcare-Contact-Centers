"""Dialogflow CX client for conversation management."""

from typing import Dict, Any, Optional, List
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.api_core.exceptions import GoogleAPIError

from config.config import config
from src.utils.logging import get_logger

logger = get_logger(__name__)


class DialogflowClient:
    """Client for interacting with Dialogflow CX."""
    
    def __init__(self, project_id: str = None, location: str = None, agent_id: str = None):
        """Initialize Dialogflow client.
        
        Args:
            project_id: GCP project ID
            location: GCP location
            agent_id: Dialogflow agent ID
        """
        self.project_id = project_id or config.gcp.project_id
        self.location = location or config.gcp.location
        self.agent_id = agent_id or config.gcp.dialogflow_agent_id
        
        # Initialize clients
        self.sessions_client = dialogflow.SessionsClient()
        self.agents_client = dialogflow.AgentsClient()
        
        logger.info("Dialogflow client initialized", {
            "project_id": self.project_id,
            "location": self.location
        })
    
    def detect_intent(
        self,
        session_id: str,
        text: str,
        language_code: str = "en"
    ) -> Dict[str, Any]:
        """Detect intent from user input.
        
        Args:
            session_id: Unique session identifier
            text: User input text
            language_code: Language code (default: en)
            
        Returns:
            Dict containing intent detection results
        """
        try:
            session_path = self.sessions_client.session_path(
                self.project_id,
                self.location,
                self.agent_id,
                session_id
            )
            
            text_input = dialogflow.TextInput(text=text)
            query_input = dialogflow.QueryInput(
                text=text_input,
                language_code=language_code
            )
            
            request = dialogflow.DetectIntentRequest(
                session=session_path,
                query_input=query_input
            )
            
            response = self.sessions_client.detect_intent(request=request)
            
            result = {
                "response_id": response.response_id,
                "query_text": response.query_result.text,
                "intent": {
                    "name": response.query_result.intent.display_name,
                    "confidence": response.query_result.intent_detection_confidence,
                },
                "parameters": dict(response.query_result.parameters),
                "fulfillment_messages": [
                    msg.text.text[0] if msg.text.text else ""
                    for msg in response.query_result.response_messages
                ],
                "current_page": response.query_result.current_page.display_name,
            }
            
            logger.info("Intent detected", {
                "session_id": session_id,
                "intent": result["intent"]["name"],
                "confidence": result["intent"]["confidence"]
            })
            
            return result
            
        except GoogleAPIError as e:
            logger.error(f"Dialogflow API error: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error detecting intent: {e}", exc_info=True)
            raise
    
    def stream_detect_intent(
        self,
        session_id: str,
        audio_chunks: List[bytes],
        language_code: str = "en",
        sample_rate: int = 16000
    ):
        """Stream audio for intent detection (for voice calls).
        
        Args:
            session_id: Unique session identifier
            audio_chunks: List of audio byte chunks
            language_code: Language code
            sample_rate: Audio sample rate in Hz
            
        Yields:
            Intent detection results
        """
        try:
            session_path = self.sessions_client.session_path(
                self.project_id,
                self.location,
                self.agent_id,
                session_id
            )
            
            def request_generator():
                # First request with session and config
                audio_config = dialogflow.InputAudioConfig(
                    audio_encoding=dialogflow.AudioEncoding.LINEAR16,
                    sample_rate_hertz=sample_rate,
                    language_code=language_code
                )
                query_input = dialogflow.QueryInput(
                    audio=audio_config,
                    language_code=language_code
                )
                
                yield dialogflow.StreamingDetectIntentRequest(
                    session=session_path,
                    query_input=query_input
                )
                
                # Subsequent requests with audio chunks
                for chunk in audio_chunks:
                    yield dialogflow.StreamingDetectIntentRequest(
                        input_audio=chunk
                    )
            
            responses = self.sessions_client.streaming_detect_intent(
                requests=request_generator()
            )
            
            for response in responses:
                if response.recognition_result:
                    yield {
                        "transcript": response.recognition_result.transcript,
                        "is_final": response.recognition_result.is_final,
                        "confidence": response.recognition_result.confidence
                    }
                
                if response.detect_intent_response:
                    query_result = response.detect_intent_response.query_result
                    yield {
                        "intent": query_result.intent.display_name,
                        "confidence": query_result.intent_detection_confidence,
                        "fulfillment": [
                            msg.text.text[0] if msg.text.text else ""
                            for msg in query_result.response_messages
                        ]
                    }
        
        except GoogleAPIError as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            raise
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get current session information.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information
        """
        session_path = self.sessions_client.session_path(
            self.project_id,
            self.location,
            self.agent_id,
            session_id
        )
        
        return {
            "session_id": session_id,
            "session_path": session_path,
        }
