# MedAssist Web Interface

A production-ready web interface for the MedAssist Healthcare Insurance Agent.

## 🚀 Quick Start

### Start the Web Server

```bash
source .venv/bin/activate
python web_api.py
```

The server will start on `http://localhost:5000`

### Access the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

## 📚 API Endpoints

### 1. Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "nodes": {...},
  "timestamp": "2026-02-18T..."
}
```

### 2. Process Query
```http
POST /api/query
Content-Type: application/json

{
  "query": "Is diabetes covered at Apollo Bangalore?",
  "customer_id": "CUST0001"
}
```

Response:
```json
{
  "query": "Is diabetes covered at Apollo Bangalore?",
  "customer_id": "CUST0001",
  "response": "Yes, your Gold Shield plan covers...",
  "timestamp": "2026-02-18T..."
}
```

### 3. Get Statistics
```http
GET /api/stats
```

Response:
```json
{
  "total_nodes": {...},
  "total_relationships": 248,
  "customer_count": 10,
  "policy_count": 5,
  ...
}
```

### 4. List Customers
```http
GET /api/customers
```

Response:
```json
{
  "customers": [
    {"id": "CUST0001", "name": "Rajesh Kumar", "city": "Jaipur", "age": 45},
    ...
  ],
  "count": 10
}
```

### 5. Get Schema
```http
GET /api/schema
```

Returns the knowledge graph schema information.

## 🧪 Testing

Run the API tests:
```bash
source .venv/bin/activate
python test_web_api.py
```

Expected output:
```
Test Results: 5 passed, 0 failed
```

## 🎨 Features

- **Beautiful UI**: Modern, responsive chat interface
- **Real-time Interaction**: Async API calls with typing indicators
- **Customer Selection**: Select from 10 sample customers
- **Example Queries**: Quick-start examples
- **Live Statistics**: Real-time database stats
- **Error Handling**: Graceful error messages
- **CORS Enabled**: Ready for frontend integration

## 🔧 Configuration

The web API uses the same configuration as the rest of the application:
- `.env` file for Neo4j and Gemini credentials
- Default port: 5000
- Host: 0.0.0.0 (accessible from network)

## 📱 Usage Examples

### Using cURL

```bash
# Health check
curl http://localhost:5000/health

# Query with customer ID
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Is diabetes covered?","customer_id":"CUST0001"}'

# Get statistics
curl http://localhost:5000/api/stats

# List customers
curl http://localhost:5000/api/customers
```

### Using Python

```python
import requests

# Query the agent
response = requests.post('http://localhost:5000/api/query', json={
    'query': 'Show me hospitals in Bangalore',
    'customer_id': 'CUST0001'
})

print(response.json()['response'])
```

### Using JavaScript

```javascript
// Query the agent
fetch('http://localhost:5000/api/query', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        query: 'Is Metformin covered?',
        customer_id: 'CUST0001'
    })
})
.then(res => res.json())
.then(data => console.log(data.response));
```

## 🛠️ Development

To run in development mode with auto-reload:

```python
# In web_api.py, change:
app.run(debug=True)
```

## 🚢 Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_api:app
```

Or with Docker:

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web_api:app"]
```

## 📊 Performance

- Average response time: ~3-4 seconds (includes LLM processing)
- Concurrent requests: Supported with threading
- Rate limiting: Not implemented (add with Flask-Limiter if needed)

## 🔐 Security

Current implementation includes:
- ✅ CORS enabled for all origins (configure for production)
- ✅ Input validation
- ✅ Error handling
- ✅ Logging

For production, consider adding:
- [ ] Authentication (JWT tokens)
- [ ] Rate limiting
- [ ] HTTPS/TLS
- [ ] API keys
- [ ] Request logging to database

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill existing process
pkill -f "python web_api.py"

# Or use a different port
# In web_api.py: app.run(port=5001)
```

### Database connection failed
```bash
# Check Neo4j connection
python -c "from neo4j_connector import Neo4jConnector; c = Neo4jConnector(); print(c.connect())"
```

### Agent slow to respond
- First query is slower due to agent initialization
- Subsequent queries are faster
- Consider implementing caching for common queries

## 📝 License

MIT License - Same as main project

---

**Built with**: Flask + LangGraph + Neo4j + Gemini 2.0 Flash  
**Status**: Production-ready ✅  
**Last Updated**: February 18, 2026
