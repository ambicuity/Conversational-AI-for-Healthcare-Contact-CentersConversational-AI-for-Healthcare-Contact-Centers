# Architecture Deep Dive

## System Architecture

### High-Level Components

The Healthcare Conversational AI Platform consists of several interconnected components:

1. **API Gateway Layer** (Flask)
   - REST API endpoints
   - Webhook handlers
   - Request validation
   - Authentication/authorization

2. **Conversation Orchestration** (Dialogflow CX)
   - Intent detection
   - Entity extraction
   - Multi-turn conversation flows
   - Context management

3. **Intelligence Layer** (Gemini LLM)
   - Conversation summarization
   - Smart reply generation
   - Intent clarification
   - Knowledge snippet generation

4. **Agent Assist Service**
   - Real-time conversation tracking
   - Async processing for low latency
   - Suggestion generation
   - Next-best action recommendations

5. **Integration Layer**
   - Genesys Cloud (contact center)
   - CRM (Salesforce)
   - Event streaming (Pub/Sub)

6. **Infrastructure** (GCP)
   - Compute (Cloud Run/GKE)
   - Storage (Cloud Storage)
   - Secrets (Secret Manager)
   - Monitoring (Cloud Logging)

## Component Interactions

### Patient Self-Service Flow

```
┌──────────┐
│ Patient  │
└────┬─────┘
     │ 1. Initiates contact (voice/chat)
     ▼
┌────────────────┐
│  Genesys Cloud │
└────┬───────────┘
     │ 2. Routes to AI bot
     ▼
┌────────────────────┐
│  Dialogflow CX     │
│  - Detect intent   │
│  - Extract entities│
│  - Manage flow     │
└────┬───────────────┘
     │ 3. Webhook call (if needed)
     ▼
┌────────────────────┐
│  Flask Application │
│  - Process request │
│  - Call CRM        │
└────┬───────────────┘
     │ 4. CRM operation
     ▼
┌────────────────────┐
│  CRM (Salesforce)  │
│  - Fetch data      │
│  - Create records  │
└────┬───────────────┘
     │ 5. Response
     ▼
Back to Dialogflow → Genesys → Patient
```

### Agent Assist Flow

```
┌────────────────┐
│ Agent + Patient│
│  in live chat  │
└────┬───────────┘
     │ 1. Messages exchanged
     ▼
┌────────────────────┐
│  Genesys Cloud     │
│  - Webhook events  │
└────┬───────────────┘
     │ 2. Send events
     ▼
┌────────────────────────────┐
│  Flask Webhook Handler     │
│  - Validate signature      │
│  - Parse event             │
│  - Update conversation     │
└────┬───────────────────────┘
     │ 3. Trigger Agent Assist
     ▼
┌────────────────────────────┐
│  Agent Assist Service      │
│  - Track conversation      │
│  - Trigger async processing│
└────┬───────────────────────┘
     │ 4. Request LLM services
     ▼
┌────────────────────────────┐
│  Gemini LLM Service        │
│  - Redact PHI              │
│  - Generate summaries      │
│  - Create smart replies    │
│  - Generate knowledge      │
└────┬───────────────────────┘
     │ 5. Return suggestions
     ▼
┌────────────────────────────┐
│  Agent UI (Genesys)        │
│  - Display summary         │
│  - Show smart replies      │
│  - Present knowledge       │
└────────────────────────────┘
```

## Data Models

### Conversation Message
```python
{
  "role": "patient|agent|system",
  "text": "message content",
  "timestamp": "ISO-8601 datetime"
}
```

### Agent Assist Response
```python
{
  "conversation_id": "conv-123",
  "timestamp": "ISO-8601",
  "summary": "Bullet point summary...",
  "smart_replies": [
    {
      "text": "Suggested response",
      "confidence": 0.85
    }
  ],
  "knowledge_snippets": [
    {
      "snippet": "Relevant knowledge",
      "relevance_score": 0.90
    }
  ],
  "next_best_action": "Action recommendation",
  "confidence_score": 0.82
}
```

## Scalability Considerations

### Horizontal Scaling
- Flask application is stateless
- Multiple instances can run behind load balancer
- Session data stored externally (Redis/Firestore)

### Async Processing
- Agent Assist uses async/await for concurrent operations
- Pub/Sub for decoupled event processing
- Celery for background tasks (optional)

### Caching Strategy
- Conversation context cached for active sessions
- CRM responses cached with TTL
- LLM responses cached for identical inputs

## Security Architecture

### Defense in Depth

1. **Network Layer**
   - TLS 1.2+ for all connections
   - Private VPC for internal services
   - Cloud Armor for DDoS protection

2. **Application Layer**
   - Input validation
   - Request rate limiting
   - CORS configuration
   - Webhook signature verification

3. **Data Layer**
   - PHI redaction before LLM processing
   - Encryption at rest
   - Minimal data retention
   - Audit logging

4. **Authentication/Authorization**
   - OAuth 2.0 for API access
   - Service accounts with minimal permissions
   - Secret Manager for credentials
   - JWT for session management

## Performance Optimization

### Latency Targets
- Intent detection: < 500ms
- Agent Assist generation: < 2s
- Webhook processing: < 1s

### Optimization Techniques
1. **Parallel Processing**: Multiple LLM operations run concurrently
2. **Context Window Management**: Only send necessary conversation history
3. **Connection Pooling**: Reuse HTTP connections to external services
4. **Selective Processing**: Only trigger Agent Assist when needed

## Monitoring & Observability

### Metrics
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Active conversations count
- LLM token usage
- CRM API call volume

### Logging
- Structured JSON logs
- No PHI in logs (sanitized)
- Request/response correlation IDs
- Audit trail for compliance

### Alerting
- Error rate spikes
- Latency degradation
- Service availability
- Quota/rate limit warnings

## Disaster Recovery

### Backup Strategy
- Daily snapshots of configuration
- CRM data replicated by CRM provider
- Conversation logs archived to Cloud Storage

### Failover
- Multi-region deployment (optional)
- Automatic health checks with restart
- Graceful degradation (disable Agent Assist if LLM unavailable)

## Cost Optimization

### Resource Efficiency
- Cloud Run auto-scales to zero
- Spot VMs for non-critical workloads
- Committed use discounts for steady state
- LLM prompt optimization to reduce tokens

### Monitoring Costs
- Budget alerts
- Cost allocation by service
- Regular cost review and optimization
