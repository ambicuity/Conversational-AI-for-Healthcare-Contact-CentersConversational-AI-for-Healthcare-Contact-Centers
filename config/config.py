"""Configuration management for Healthcare Conversational AI Platform."""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class GCPConfig:
    """Google Cloud Platform configuration."""
    project_id: str
    location: str = "us-central1"
    dialogflow_agent_id: Optional[str] = None
    gemini_model: str = "gemini-pro"
    pubsub_topic: Optional[str] = None


@dataclass
class GenesysConfig:
    """Genesys Cloud configuration."""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    environment: str = "mypurecloud.com"
    webhook_secret: Optional[str] = None


@dataclass
class CRMConfig:
    """CRM integration configuration."""
    provider: str = "salesforce"
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None


@dataclass
class SecurityConfig:
    """Security and compliance configuration."""
    enable_phi_redaction: bool = True
    enable_audit_logging: bool = True
    jwt_secret: Optional[str] = None
    allowed_origins: list = None

    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = ["*"]


@dataclass
class AppConfig:
    """Main application configuration."""
    environment: str
    gcp: GCPConfig
    genesys: GenesysConfig
    crm: CRMConfig
    security: SecurityConfig
    
    # Service settings
    agent_assist_enabled: bool = True
    llm_confidence_threshold: float = 0.7
    max_conversation_history: int = 10
    
    # Performance settings
    request_timeout: int = 30
    max_retries: int = 3
    enable_caching: bool = True


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    environment = os.getenv("ENVIRONMENT", "development")
    
    gcp_config = GCPConfig(
        project_id=os.getenv("GCP_PROJECT_ID", "healthcare-ai-project"),
        location=os.getenv("GCP_LOCATION", "us-central1"),
        dialogflow_agent_id=os.getenv("DIALOGFLOW_AGENT_ID"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-pro"),
        pubsub_topic=os.getenv("PUBSUB_TOPIC", "conversation-events"),
    )
    
    genesys_config = GenesysConfig(
        client_id=os.getenv("GENESYS_CLIENT_ID"),
        client_secret=os.getenv("GENESYS_CLIENT_SECRET"),
        environment=os.getenv("GENESYS_ENVIRONMENT", "mypurecloud.com"),
        webhook_secret=os.getenv("GENESYS_WEBHOOK_SECRET"),
    )
    
    crm_config = CRMConfig(
        provider=os.getenv("CRM_PROVIDER", "salesforce"),
        api_endpoint=os.getenv("CRM_API_ENDPOINT"),
        api_key=os.getenv("CRM_API_KEY"),
    )
    
    security_config = SecurityConfig(
        enable_phi_redaction=os.getenv("ENABLE_PHI_REDACTION", "true").lower() == "true",
        enable_audit_logging=os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true",
        jwt_secret=os.getenv("JWT_SECRET"),
        allowed_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    )
    
    return AppConfig(
        environment=environment,
        gcp=gcp_config,
        genesys=genesys_config,
        crm=crm_config,
        security=security_config,
        agent_assist_enabled=os.getenv("AGENT_ASSIST_ENABLED", "true").lower() == "true",
        llm_confidence_threshold=float(os.getenv("LLM_CONFIDENCE_THRESHOLD", "0.7")),
        max_conversation_history=int(os.getenv("MAX_CONVERSATION_HISTORY", "10")),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
    )


# Global config instance
config = load_config()
