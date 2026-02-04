# API Examples

## Patient Self-Service Examples

### Example 1: Schedule Appointment

**Request to Dialogflow:**
```bash
curl -X POST https://your-service.com/api/v1/conversations/detect-intent \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "patient-12345",
    "text": "I need to schedule an appointment",
    "language_code": "en"
  }'
```

**Response:**
```json
{
  "response_id": "abc123",
  "query_text": "I need to schedule an appointment",
  "intent": {
    "name": "appointment.schedule",
    "confidence": 0.95
  },
  "parameters": {},
  "fulfillment_messages": [
    "I can help you with your appointment. What type of appointment do you need?"
  ],
  "current_page": "collect_appointment_type"
}
```

### Example 2: Check Insurance Coverage

**Webhook Request (from Dialogflow):**
```json
{
  "sessionInfo": {
    "session": "projects/PROJECT/locations/LOCATION/agents/AGENT/sessions/SESSION",
    "parameters": {
      "patient_id": "P123456",
      "insurance_topic": "coverage"
    }
  },
  "fulfillmentInfo": {
    "tag": "insurance_lookup"
  }
}
```

**Webhook Response:**
```json
{
  "fulfillmentResponse": {
    "messages": [
      {
        "text": {
          "text": [
            "You have PPO coverage with BlueCross BlueShield. Your plan is currently active."
          ]
        }
      }
    ]
  }
}
```

## Agent Assist Examples

### Example 3: Get Real-Time Agent Assist

**Setup Conversation:**
```bash
# Add patient message
curl -X POST https://your-service.com/api/v1/conversations/conv-789/messages \
  -H "Content-Type: application/json" \
  -d '{
    "role": "patient",
    "text": "I received a bill for $500 but my insurance should cover this"
  }'

# Add agent greeting
curl -X POST https://your-service.com/api/v1/conversations/conv-789/messages \
  -H "Content-Type: application/json" \
  -d '{
    "role": "agent",
    "text": "Hello, I understand you have a billing question. Let me help you with that."
  }'
```

**Request Agent Assist:**
```bash
curl -X POST https://your-service.com/api/v1/agent-assist \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv-789",
    "include_summary": true,
    "include_smart_replies": true,
    "include_knowledge": true
  }'
```

**Response:**
```json
{
  "conversation_id": "conv-789",
  "timestamp": "2024-02-04T18:30:00Z",
  "summary": "• Patient inquiring about $500 bill\n• Believes insurance should cover\n• Agent acknowledged and offered assistance",
  "smart_replies": [
    {
      "text": "I'd be happy to look into this for you. Can you provide your insurance policy number?",
      "confidence": 0.87
    },
    {
      "text": "Let me pull up your account. What's your date of birth for verification?",
      "confidence": 0.82
    },
    {
      "text": "I'll check your insurance coverage and the bill details. One moment please.",
      "confidence": 0.79
    }
  ],
  "knowledge_snippets": [
    {
      "snippet": "For billing disputes: Always verify patient identity first, then check insurance claim status in CRM before discussing specifics.",
      "relevance_score": 0.85
    }
  ],
  "next_best_action": "Look up patient billing information",
  "confidence_score": 0.83
}
```

### Example 4: Genesys Webhook Event

**Incoming Webhook (Message Received):**
```bash
curl -X POST https://your-service.com/webhooks/genesys \
  -H "Content-Type: application/json" \
  -H "X-Genesys-Signature: abc123..." \
  -d '{
    "topicName": "v2.conversations.messages.created",
    "conversationId": "conv-456",
    "message": {
      "id": "msg-789",
      "type": "customer",
      "text": "I need to refill my prescription",
      "timestamp": "2024-02-04T18:30:00Z"
    }
  }'
```

**Response:**
```json
{
  "status": "processed",
  "conversation_id": "conv-456",
  "message_role": "patient"
}
```

## CRM Integration Examples

### Example 5: Get Patient Information

```python
from src.crm.provider import CRMFactory

# Initialize CRM client
crm = CRMFactory.create_crm(
    provider="salesforce",
    api_endpoint="https://your-instance.salesforce.com",
    api_key="your-api-key"
)

# Get patient info
patient_info = crm.get_patient_info("P123456")
print(patient_info)
```

**Output:**
```python
{
    "patient_id": "P123456",
    "name": "John Doe",
    "email": "[REDACTED_EMAIL]",
    "phone": "[REDACTED_PHONE]",
    "date_of_birth": "[REDACTED_DATE]",
    "insurance_provider": "BlueCross BlueShield",
    "primary_care_physician": "Dr. Sarah Johnson"
}
```

### Example 6: Schedule Appointment

```python
appointment = crm.schedule_appointment(
    patient_id="P123456",
    appointment_type="checkup",
    datetime_str="2024-03-15T10:00:00Z",
    provider_id="DR789",
    notes="Annual physical exam"
)
print(appointment)
```

**Output:**
```python
{
    "appointment_id": "appt_P123456_1707068400.123",
    "patient_id": "P123456",
    "type": "checkup",
    "datetime": "2024-03-15T10:00:00Z",
    "provider_id": "DR789",
    "notes": "Annual physical exam",
    "status": "scheduled",
    "created_at": "2024-02-04T18:30:00Z"
}
```

## Testing Examples

### Example 7: Test PHI Redaction

```python
from src.utils.phi_redaction import phi_redactor

# Test text with PHI
text = "Patient SSN is 123-45-6789, call at 555-123-4567"

# Redact PHI
redacted_text, counts = phi_redactor.redact(text)

print(f"Original: {text}")
print(f"Redacted: {redacted_text}")
print(f"Redaction counts: {counts}")
```

**Output:**
```
Original: Patient SSN is 123-45-6789, call at 555-123-4567
Redacted: Patient SSN is [REDACTED_SSN], call at [REDACTED_PHONE]
Redaction counts: {'ssn': 1, 'phone': 1}
```

### Example 8: Test LLM Service

```python
from src.llm_services.gemini_service import gemini_service

# Create conversation
messages = [
    {"role": "patient", "text": "I need to reschedule my appointment"},
    {"role": "agent", "text": "I can help with that. When would you like to reschedule?"},
    {"role": "patient", "text": "Next Tuesday morning if possible"}
]

# Generate summary
summary_result = gemini_service.summarize_conversation(messages)
print(summary_result['summary'])

# Generate smart replies
replies_result = gemini_service.generate_smart_replies(
    context_messages=messages[:-1],
    last_message=messages[-1]['text']
)

for reply in replies_result['replies']:
    print(f"- {reply['text']} (confidence: {reply['confidence']})")
```

## Complete Conversation Flow Example

### Example 9: End-to-End Appointment Scheduling

```bash
# Step 1: Patient initiates conversation
curl -X POST https://your-service.com/api/v1/conversations/detect-intent \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-001",
    "text": "I want to book an appointment"
  }'

# Step 2: System asks for type
# Response includes: "What type of appointment?"

# Step 3: Patient specifies type
curl -X POST https://your-service.com/api/v1/conversations/detect-intent \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-001",
    "text": "Annual checkup"
  }'

# Step 4: System asks for date/time
# Response includes: "When would you like to schedule?"

# Step 5: Patient provides date/time
curl -X POST https://your-service.com/api/v1/conversations/detect-intent \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-001",
    "text": "Next Monday at 10am"
  }'

# Step 6: Dialogflow calls webhook to book appointment
# Webhook creates appointment in CRM
# Response: "Your checkup is scheduled for Monday, Feb 12 at 10:00 AM. Confirmation: APPT-12345"
```

## Monitoring Examples

### Example 10: Get Platform Metrics

```bash
curl -X GET https://your-service.com/api/v1/metrics
```

**Response:**
```json
{
  "agent_assist": {
    "active_conversations": 5,
    "total_messages": 42,
    "avg_messages_per_conversation": 8.4
  },
  "timestamp": "2024-02-04T18:30:00Z"
}
```

### Example 11: Health Check

```bash
curl -X GET https://your-service.com/health
```

**Response:**
```json
{
  "status": "healthy",
  "environment": "production",
  "services": {
    "dialogflow": "ready",
    "gemini": "ready",
    "agent_assist": "ready",
    "genesys": "ready",
    "crm": "ready"
  }
}
```

## Error Handling Examples

### Example 12: Invalid Request

```bash
curl -X POST https://your-service.com/api/v1/agent-assist \
  -H "Content-Type: application/json" \
  -d '{}'  # Missing conversation_id
```

**Response:**
```json
{
  "error": "Missing conversation_id"
}
```
HTTP Status: 400

### Example 13: Service Error

**Response:**
```json
{
  "error": "Internal server error"
}
```
HTTP Status: 500

## Integration Testing

### Example 14: Test Complete Flow with Mock Services

```python
import pytest
from app import app

def test_complete_appointment_flow():
    """Test end-to-end appointment scheduling."""
    client = app.test_client()
    
    # Step 1: Detect initial intent
    response = client.post('/api/v1/conversations/detect-intent', json={
        'session_id': 'test-session',
        'text': 'I need an appointment'
    })
    assert response.status_code == 200
    
    # Step 2: Add conversation messages
    client.post('/api/v1/conversations/test-conv/messages', json={
        'role': 'patient',
        'text': 'I need an appointment'
    })
    
    # Step 3: Get agent assist
    response = client.post('/api/v1/agent-assist', json={
        'conversation_id': 'test-conv',
        'include_summary': True
    })
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'summary' in data or 'smart_replies' in data
```

---

For more examples and detailed API documentation, see the [docs/README.md](README.md) file.
