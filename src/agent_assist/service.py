"""Real-time conversation tracking and assistance"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import asyncio

from src.llm_services.gemini_service import gemini_service
from src.utils.logging import get_logger
from src.utils import utcnow

logger = get_logger(__name__)


@dataclass
class AgentAssistResponse:
    """Response from Agent Assist system."""
    conversation_id: str
    timestamp: str
    summary: Optional[str] = None
    smart_replies: Optional[List[Dict[str, Any]]] = None
    knowledge_snippets: Optional[List[Dict[str, Any]]] = None
    next_best_action: Optional[str] = None
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class AgentAssistService:
    """Real-time agent assistance service."""
    
    def __init__(self):
        """Initialize Agent Assist service."""
        self.active_conversations: Dict[str, List[Dict]] = {}
        self.llm_service = gemini_service
        logger.info("Agent Assist service initialized")
    
    def register_conversation(self, conversation_id: str):
        """Register a new conversation for tracking.
        
        Args:
            conversation_id: Unique conversation identifier
        """
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = []
            logger.info(f"Registered conversation: {conversation_id}")
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        text: str,
        timestamp: Optional[str] = None
    ):
        """Add a message to conversation history.
        
        Args:
            conversation_id: Conversation identifier
            role: Message role (agent, patient, system)
            text: Message text
            timestamp: Message timestamp
        """
        if conversation_id not in self.active_conversations:
            self.register_conversation(conversation_id)
        
        message = {
            "role": role,
            "text": text,
            "timestamp": timestamp or utcnow().isoformat()
        }
        
        self.active_conversations[conversation_id].append(message)
        logger.debug(f"Message added to conversation {conversation_id}")
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get conversation history.
        
        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of recent messages to return
            
        Returns:
            List of conversation messages
        """
        messages = self.active_conversations.get(conversation_id, [])
        if limit:
            return messages[-limit:]
        return messages
    
    async def generate_real_time_assist(
        self,
        conversation_id: str,
        include_summary: bool = True,
        include_smart_replies: bool = True,
        include_knowledge: bool = True
    ) -> AgentAssistResponse:
        """Generate comprehensive real-time assistance.
        
        This method runs asynchronously to minimize latency impact.
        
        Args:
            conversation_id: Conversation identifier
            include_summary: Generate conversation summary
            include_smart_replies: Generate smart reply suggestions
            include_knowledge: Generate knowledge snippets
            
        Returns:
            AgentAssistResponse with assistance data
        """
        try:
            messages = self.get_conversation_history(conversation_id)
            
            if not messages:
                logger.warning(f"No messages found for conversation {conversation_id}")
                return AgentAssistResponse(
                    conversation_id=conversation_id,
                    timestamp=utcnow().isoformat()
                )
            
            # Run assist operations concurrently for speed
            tasks = []
            
            # Summary generation
            summary_task = None
            if include_summary and len(messages) >= 3:
                summary_task = asyncio.create_task(
                    self._generate_summary_async(messages)
                )
                tasks.append(("summary", summary_task))
            
            # Smart replies generation
            smart_replies_task = None
            if include_smart_replies and len(messages) >= 2:
                last_patient_message = self._get_last_patient_message(messages)
                if last_patient_message:
                    smart_replies_task = asyncio.create_task(
                        self._generate_smart_replies_async(
                            messages[:-1],
                            last_patient_message
                        )
                    )
                    tasks.append(("smart_replies", smart_replies_task))
            
            # Knowledge snippets
            knowledge_task = None
            if include_knowledge:
                last_patient_message = self._get_last_patient_message(messages)
                if last_patient_message:
                    knowledge_task = asyncio.create_task(
                        self._generate_knowledge_async(last_patient_message)
                    )
                    tasks.append(("knowledge", knowledge_task))
            
            # Wait for all tasks
            results = {}
            for task_name, task in tasks:
                try:
                    results[task_name] = await task
                except Exception as e:
                    logger.error(f"Error in {task_name} task: {e}")
                    results[task_name] = None
            
            # Build response
            response = AgentAssistResponse(
                conversation_id=conversation_id,
                timestamp=utcnow().isoformat(),
                summary=results.get("summary"),
                smart_replies=results.get("smart_replies"),
                knowledge_snippets=results.get("knowledge"),
                next_best_action=self._determine_next_best_action(messages),
                confidence_score=self._calculate_overall_confidence(results)
            )
            
            logger.info(f"Agent assist generated for conversation {conversation_id}")
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating agent assist: {e}", exc_info=True)
            raise
    
    async def _generate_summary_async(self, messages: List[Dict]) -> str:
        """Generate summary asynchronously."""
        result = self.llm_service.summarize_conversation(messages)
        return result["summary"]
    
    async def _generate_smart_replies_async(
        self,
        context_messages: List[Dict],
        last_message: str
    ) -> List[Dict[str, Any]]:
        """Generate smart replies asynchronously."""
        result = self.llm_service.generate_smart_replies(
            context_messages,
            last_message
        )
        return result["replies"]
    
    async def _generate_knowledge_async(self, query: str) -> List[Dict[str, Any]]:
        """Generate knowledge snippets asynchronously."""
        result = self.llm_service.generate_knowledge_snippet(query)
        return [result]
    
    def _get_last_patient_message(self, messages: List[Dict]) -> Optional[str]:
        """Get the last message from patient."""
        for message in reversed(messages):
            if message["role"] == "patient":
                return message["text"]
        return None
    
    def _determine_next_best_action(self, messages: List[Dict]) -> str:
        """Determine next best action based on conversation.
        
        This is a simple heuristic-based approach. In production,
        this could use ML models trained on successful resolution patterns.
        
        Args:
            messages: Conversation messages
            
        Returns:
            Next best action recommendation
        """
        if not messages:
            return "Greet patient and ask how you can help"
        
        last_message = messages[-1]["text"].lower()
        
        # Simple keyword-based suggestions
        if any(word in last_message for word in ["appointment", "schedule", "book"]):
            return "Offer available appointment slots"
        elif any(word in last_message for word in ["bill", "charge", "cost", "insurance"]):
            return "Look up patient billing information"
        elif any(word in last_message for word in ["prescription", "medication", "refill"]):
            return "Check prescription status and process refill"
        elif any(word in last_message for word in ["results", "test", "lab"]):
            return "Verify results are available and offer to send securely"
        elif any(word in last_message for word in ["speak", "talk", "representative", "person"]):
            return "Prepare for escalation to specialized team"
        else:
            return "Clarify patient's primary concern"
    
    def _calculate_overall_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate overall confidence score.
        
        Args:
            results: Dictionary of assist results
            
        Returns:
            Overall confidence score (0-1)
        """
        scores = []
        
        # Smart replies confidence
        if results.get("smart_replies"):
            avg_confidence = sum(
                r["confidence"] for r in results["smart_replies"]
            ) / len(results["smart_replies"])
            scores.append(avg_confidence)
        
        # Knowledge confidence
        if results.get("knowledge"):
            scores.append(0.85)  # Placeholder
        
        # Summary confidence
        if results.get("summary"):
            scores.append(0.90)  # Placeholder
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def close_conversation(self, conversation_id: str):
        """Close and archive conversation.
        
        Args:
            conversation_id: Conversation identifier
        """
        if conversation_id in self.active_conversations:
            del self.active_conversations[conversation_id]
            logger.info(f"Closed conversation: {conversation_id}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Agent Assist performance metrics.
        
        Returns:
            Performance metrics
        """
        return {
            "active_conversations": len(self.active_conversations),
            "total_messages": sum(
                len(msgs) for msgs in self.active_conversations.values()
            ),
            "avg_messages_per_conversation": (
                sum(len(msgs) for msgs in self.active_conversations.values()) /
                len(self.active_conversations)
                if self.active_conversations else 0
            )
        }


# Singleton instance
agent_assist_service = AgentAssistService()
