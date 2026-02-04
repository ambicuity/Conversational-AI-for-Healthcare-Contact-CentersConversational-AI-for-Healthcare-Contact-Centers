"""Tests for Agent Assist service."""

import pytest
import asyncio
from src.agent_assist.service import AgentAssistService


@pytest.fixture
def agent_assist():
    """Create Agent Assist service instance."""
    return AgentAssistService()


def test_register_conversation(agent_assist):
    """Test conversation registration."""
    conversation_id = "test-conv-1"
    agent_assist.register_conversation(conversation_id)
    
    assert conversation_id in agent_assist.active_conversations
    assert len(agent_assist.active_conversations[conversation_id]) == 0


def test_add_message(agent_assist):
    """Test adding messages to conversation."""
    conversation_id = "test-conv-2"
    
    agent_assist.add_message(conversation_id, "patient", "I need help")
    agent_assist.add_message(conversation_id, "agent", "How can I assist you?")
    
    messages = agent_assist.get_conversation_history(conversation_id)
    assert len(messages) == 2
    assert messages[0]["role"] == "patient"
    assert messages[1]["role"] == "agent"


def test_get_conversation_history_with_limit(agent_assist):
    """Test conversation history with limit."""
    conversation_id = "test-conv-3"
    
    for i in range(10):
        agent_assist.add_message(conversation_id, "patient", f"Message {i}")
    
    messages = agent_assist.get_conversation_history(conversation_id, limit=5)
    assert len(messages) == 5


def test_close_conversation(agent_assist):
    """Test closing conversation."""
    conversation_id = "test-conv-4"
    
    agent_assist.register_conversation(conversation_id)
    assert conversation_id in agent_assist.active_conversations
    
    agent_assist.close_conversation(conversation_id)
    assert conversation_id not in agent_assist.active_conversations


def test_get_metrics(agent_assist):
    """Test metrics retrieval."""
    agent_assist.register_conversation("conv-1")
    agent_assist.add_message("conv-1", "patient", "Hello")
    
    metrics = agent_assist.get_metrics()
    
    assert "active_conversations" in metrics
    assert metrics["active_conversations"] >= 1


def test_determine_next_best_action(agent_assist):
    """Test next best action determination."""
    conversation_id = "test-conv-5"
    
    agent_assist.add_message(conversation_id, "patient", "I need to schedule an appointment")
    
    messages = agent_assist.get_conversation_history(conversation_id)
    action = agent_assist._determine_next_best_action(messages)
    
    assert "appointment" in action.lower()
