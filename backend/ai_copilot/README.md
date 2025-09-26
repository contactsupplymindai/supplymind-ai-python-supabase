# AI Copilot Microservice

Intelligent AI-powered copilot microservice providing chat assistance, vector RAG, semantic search, and actionable suggestions for SupplyMind AI platform.

## Features

- 🤖 **Chat Copilot**: Conversational AI with context-aware responses
- 🧠 **Vector RAG**: Embedding generation and storage for retrieval-augmented generation
- 🔍 **Semantic Search**: Advanced similarity search across document embeddings
- ⚡ **Action Suggestions**: AI-powered workflow and optimization recommendations

## API Endpoints

### 1. Chat Copilot
`POST /api/copilot/chat/`

Conversational AI endpoint with session management and context awareness.

#### Request Body
```json
{
  "message": "How can I optimize my supply chain?",
  "session_id": "optional-uuid",
  "stream": false,
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 1000,
  "context": {
    "topic": "supply_chain",
    "user_role": "manager"
  }
}
```

#### Response
```json
{
  "response": "To optimize your supply chain, consider implementing...",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "message_id": "987fcdeb-51a2-45d6-b123-456789abcdef",
  "token_usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
  },
  "model": "gpt-4o-mini",
  "processing_time": 1.25
}
```

### 2. Vector RAG: Embedding Generation
`POST /api/copilot/embed/`

Generate and store vector embeddings for documents and content.

#### Request Body
```json
{
  "text": "This is content to be embedded for RAG.",
  "model": "text-embedding-3-small",
  "source_type": "document",
  "source_id": "doc_123",
  "metadata": {
    "category": "documentation",
    "version": "1.0"
  }
}
```

#### Response
```json
{
  "embedding_id": "456e7890-f12b-34c5-d678-901234567890",
  "vector": [0.123, -0.456, 0.789, ...],
  "model": "text-embedding-3-small",
  "token_count": 25,
  "processing_time": 0.45
}
```

### 3. Semantic Search
`POST /api/copilot/search/`

Perform semantic search across stored embeddings.

#### Request Body
```json
{
  "query": "supply chain optimization strategies",
  "top_k": 5,
  "threshold": 0.7,
  "source_types": ["document", "knowledge_base"],
  "filters": {
    "category": "best_practices"
  },
  "include_embeddings": false
}
```

#### Response
```json
{
  "results": [
    {
      "content": "Supply chain optimization involves...",
      "similarity_score": 0.92,
      "source_type": "document",
      "source_id": "doc_456",
      "metadata": {
        "category": "best_practices",
        "author": "expert"
      },
      "embedding_id": "789a0123-b45c-67d8-e901-234567890123"
    }
  ],
  "total_results": 5,
  "processing_time": 0.85
}
```

### 4. Action Suggestions
`POST /api/copilot/suggest/`

Generate AI-powered actionable suggestions based on context analysis.

#### Request Body
```json
{
  "context": {
    "errors": 25,
    "latency_ms": 750,
    "throughput": "low",
    "recent_changes": ["config_update", "db_migration"]
  },
  "suggestion_types": ["optimization", "alert", "workflow"],
  "max_suggestions": 5,
  "min_confidence": 0.6,
  "user_preferences": {
    "priority": "performance"
  }
}
```

#### Response
```json
{
  "suggestions": [
    {
      "id": "abc12345-def6-7890-gh12-345678901234",
      "suggestion_type": "optimization",
      "title": "Optimize slow queries",
      "description": "High latency detected. Suggest indexing, caching, or query optimization.",
      "priority": "medium",
      "status": "pending",
      "confidence_score": 0.75,
      "created_at": "2025-01-15T10:30:00Z",
      "context_data": {...},
      "action_payload": {
        "proposed_actions": []
      }
    }
  ],
  "total_suggestions": 3,
  "processing_time": 1.2,
  "context_analysis": {
    "keys": ["errors", "latency_ms", "throughput", "recent_changes"]
  }
}
```

## Django Models

### ChatSession
Manages conversation sessions with context and metadata.

### ChatMessage
Stores individual messages within chat sessions.

### VectorEmbedding
Stores text embeddings with metadata for semantic search.

### ActionSuggestion
Stores AI-generated suggestions with priority and status tracking.

## Installation

1. **Add to Django Settings**
   ```python
   INSTALLED_APPS = [
       # ... other apps
       'ai_copilot',
   ]
   ```

2. **Include URLs**
   ```python
   # main urls.py
   from django.urls import path, include
   
   urlpatterns = [
       # ... other patterns
       path('', include('ai_copilot.urls')),
   ]
   ```

3. **Run Migrations**
   ```bash
   python manage.py makemigrations ai_copilot
   python manage.py migrate
   ```

## Integration Setup

### OpenAI Integration
Replace stub providers in `views.py`:

```python
import openai

class LLMProvider:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def chat(self, messages, model="gpt-4o-mini", **kwargs):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return {
            "content": response.choices[0].message.content,
            "usage": response.usage.model_dump(),
            "model": response.model
        }

class EmbeddingProvider:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def embed(self, text, model="text-embedding-3-small"):
        response = self.client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
```

### HuggingFace Integration
```python
from transformers import AutoTokenizer, AutoModel
import torch

class HuggingFaceProvider:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    
    def embed(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
```

## Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_key_here

# HuggingFace Configuration (optional)
HUGGINGFACE_API_TOKEN=your_hf_token_here

# Vector Database Configuration (for production)
PGVECTOR_DATABASE_URL=postgresql://user:pass@host:5432/dbname
CHROMA_PERSIST_DIRECTORY=/path/to/chroma/data
```

## Production Considerations

1. **Vector Database**: Replace in-memory similarity with pgvector, Pinecone, or Chroma
2. **Caching**: Implement Redis caching for embeddings and frequent queries
3. **Rate Limiting**: Add rate limiting for API endpoints
4. **Monitoring**: Integrate with logging and monitoring systems
5. **Authentication**: Add proper authentication and authorization
6. **Async Processing**: Consider async processing for large embedding operations

## Usage Examples

### Python Client
```python
import requests

# Chat example
response = requests.post('http://localhost:8000/api/copilot/chat/', json={
    'message': 'Help me optimize inventory levels',
    'context': {'domain': 'supply_chain'}
})
print(response.json()['response'])

# Embedding example
response = requests.post('http://localhost:8000/api/copilot/embed/', json={
    'text': 'Inventory optimization strategies for seasonal demand',
    'source_type': 'knowledge_base'
})
embedding_id = response.json()['embedding_id']

# Search example
response = requests.post('http://localhost:8000/api/copilot/search/', json={
    'query': 'inventory management best practices',
    'top_k': 3
})
for result in response.json()['results']:
    print(f"Score: {result['similarity_score']}: {result['content'][:100]}...")
```

### JavaScript/Frontend
```javascript
// Chat integration
async function chatWithCopilot(message, sessionId = null) {
  const response = await fetch('/api/copilot/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      context: { source: 'web_app' }
    })
  });
  return await response.json();
}

// Usage
const result = await chatWithCopilot('How do I reduce supply chain costs?');
console.log(result.response);
```

## Testing

```bash
# Run tests
python manage.py test ai_copilot

# Test specific endpoint
curl -X POST http://localhost:8000/api/copilot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, AI!"}'
```

## License

Proprietary - SupplyMind AI Platform
