"""Genesys Cloud integration client."""

import requests
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from config.config import config
from src.utils.logging import get_logger
from src.utils import utcnow

logger = get_logger(__name__)


class GenesysClient:
    """Client for Genesys Cloud API integration."""
    
    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        environment: str = None
    ):
        """Initialize Genesys client.
        
        Args:
            client_id: Genesys OAuth client ID
            client_secret: Genesys OAuth client secret
            environment: Genesys environment (e.g., mypurecloud.com)
        """
        self.client_id = client_id or config.genesys.client_id
        self.client_secret = client_secret or config.genesys.client_secret
        self.environment = environment or config.genesys.environment
        
        self.base_url = f"https://api.{self.environment}/api/v2"
        self.auth_url = f"https://login.{self.environment}/oauth/token"
        
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        logger.info(f"Genesys client initialized for environment: {self.environment}")
    
    def _get_access_token(self) -> str:
        """Get OAuth access token.
        
        Returns:
            Access token
        """
        # Check if token is still valid
        if self.access_token and self.token_expires_at:
            if utcnow() < self.token_expires_at:
                return self.access_token
        
        # Request new token
        try:
            # Create basic auth header
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "client_credentials"
            }
            
            response = requests.post(
                self.auth_url,
                headers=headers,
                data=data,
                timeout=config.request_timeout
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            
            # Set expiration (with 5 minute buffer)
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = utcnow() + timedelta(seconds=expires_in - 300)
            
            logger.info("Obtained new Genesys access token")
            
            return self.access_token
        
        except requests.RequestException as e:
            logger.error(f"Error obtaining Genesys access token: {e}", exc_info=True)
            raise
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Genesys API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body
            params: Query parameters
            
        Returns:
            Response data
        """
        token = self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=config.request_timeout
            )
            response.raise_for_status()
            
            return response.json() if response.content else {}
        
        except requests.RequestException as e:
            logger.error(f"Genesys API request failed: {e}", exc_info=True)
            raise
    
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation details.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data
        """
        return self._make_request("GET", f"conversations/{conversation_id}")
    
    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get conversation messages.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum messages to retrieve
            
        Returns:
            List of messages
        """
        params = {"pageSize": limit}
        response = self._make_request(
            "GET",
            f"conversations/{conversation_id}/messages",
            params=params
        )
        return response.get("entities", [])
    
    def send_agent_assist_notification(
        self,
        conversation_id: str,
        assist_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send Agent Assist notification to agent.
        
        Args:
            conversation_id: Conversation ID
            assist_data: Agent Assist data to send
            
        Returns:
            Response data
        """
        # In production, this would use Genesys Agent Assist API
        # or custom notification mechanism
        payload = {
            "conversationId": conversation_id,
            "assistData": assist_data,
            "timestamp": utcnow().isoformat()
        }
        
        logger.info(f"Sending Agent Assist notification for conversation {conversation_id}")
        
        # This is a placeholder - actual implementation depends on Genesys setup
        return payload
    
    def wrap_up_conversation(
        self,
        conversation_id: str,
        wrap_up_code: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Apply wrap-up code to conversation.
        
        Args:
            conversation_id: Conversation ID
            wrap_up_code: Wrap-up code
            notes: Optional notes
            
        Returns:
            Response data
        """
        data = {
            "code": wrap_up_code,
            "notes": notes
        }
        
        return self._make_request(
            "PATCH",
            f"conversations/{conversation_id}/participants/wrapup",
            data=data
        )
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user (agent) information.
        
        Args:
            user_id: User ID
            
        Returns:
            User data
        """
        return self._make_request("GET", f"users/{user_id}")
    
    def search_conversations(
        self,
        start_date: str,
        end_date: str,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search conversations.
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            filters: Optional search filters
            
        Returns:
            List of conversations
        """
        query = {
            "interval": f"{start_date}/{end_date}",
            "order": "desc",
            "orderBy": "conversationStart"
        }
        
        if filters:
            query.update(filters)
        
        response = self._make_request(
            "POST",
            "analytics/conversations/details/query",
            data=query
        )
        
        return response.get("conversations", [])


# Singleton instance
genesys_client = GenesysClient()
