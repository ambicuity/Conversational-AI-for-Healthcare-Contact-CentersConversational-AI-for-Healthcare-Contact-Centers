"""Tests for Flask application endpoints."""

import pytest
from app import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'services' in data


def test_add_conversation_message(client):
    """Test adding message to conversation."""
    response = client.post(
        '/api/v1/conversations/test-conv/messages',
        json={
            'role': 'patient',
            'text': 'I need help'
        }
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'


def test_add_message_missing_fields(client):
    """Test adding message with missing fields."""
    response = client.post(
        '/api/v1/conversations/test-conv/messages',
        json={'role': 'patient'}  # Missing 'text'
    )
    
    assert response.status_code == 400


def test_get_metrics(client):
    """Test metrics endpoint."""
    response = client.get('/api/v1/metrics')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'agent_assist' in data


def test_not_found(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    
    data = response.get_json()
    assert 'error' in data
