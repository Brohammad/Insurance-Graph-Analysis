"""
MedAssist Web API - Flask REST API for Healthcare Insurance Agent
Provides HTTP endpoints for the LangGraph agent with security features
"""
from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS
from agent import MedAssistAgent
from neo4j_connector import Neo4jConnector
from security import (
    security_manager, 
    require_auth, 
    require_api_key, 
    validate_input,
    add_security_headers,
    rate_limit
)
from config import config
import os
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Configure CORS with security settings
cors_config = {
    'origins': config.CORS_ORIGINS if config.CORS_ORIGINS != ['*'] else '*',
    'methods': ['GET', 'POST', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization', 'X-API-Key'],
    'max_age': 3600
}
CORS(app, **cors_config)

# Global agent instance
agent = None
connector = None


def initialize_agent():
    """Initialize the agent and database connection"""
    global agent, connector
    try:
        # Enable vector store and memory in production
        enable_vector = config.ENVIRONMENT in ['production', 'development']
        enable_memory = config.ENVIRONMENT in ['production', 'development']
        
        agent = MedAssistAgent(
            enable_vector_store=enable_vector,
            enable_memory=enable_memory
        )
        if agent.connect():
            logger.info("✓ Agent connected to Neo4j")
            return True
        else:
            logger.error("✗ Failed to connect to Neo4j")
            return False
    except Exception as e:
        logger.error(f"✗ Error initializing agent: {e}")
        return False


# Initialize on startup
with app.app_context():
    if not initialize_agent():
        logger.warning("⚠ Agent initialization failed, will retry on first request")


# Apply security headers to all responses
@app.after_request
def apply_security_headers_middleware(response):
    """Add security headers to all responses"""
    return add_security_headers(response)


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/auth/token', methods=['POST'])
@rate_limit
def get_token():
    """
    Generate a JWT token for authentication.
    
    Request body:
    {
        "user_id": "user123",
        "api_key": "ma_xxxx..."  # Optional: API key for validation
    }
    
    Response:
    {
        "token": "eyJ...",
        "expires_in": 86400
    }
    """
    try:
        if not request.json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Sanitize user_id
        user_id = security_manager.sanitize_input(user_id, max_length=100)
        
        # Generate token
        token = security_manager.generate_token(user_id)
        
        return jsonify({
            'token': token,
            'expires_in': config.JWT_EXPIRATION_HOURS * 3600,
            'token_type': 'Bearer'
        }), 200
    
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return jsonify({'error': 'Token generation failed'}), 500


@app.route('/auth/api-key', methods=['POST'])
@rate_limit
def generate_api_key():
    """
    Generate a new API key.
    
    Request body:
    {
        "user_id": "user123"
    }
    
    Response:
    {
        "api_key": "ma_xxxx...",
        "message": "Store this securely, it won't be shown again"
    }
    """
    try:
        if not request.json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Sanitize user_id
        user_id = security_manager.sanitize_input(user_id, max_length=100)
        
        # Generate API key
        api_key = security_manager.generate_api_key(user_id)
        
        # TODO: Store hashed API key in database
        # api_key_hash = security_manager.hash_api_key(api_key)
        # store_api_key_in_db(user_id, api_key_hash)
        
        return jsonify({
            'api_key': api_key,
            'user_id': user_id,
            'message': 'Store this API key securely. It will not be shown again.'
        }), 201
    
    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        return jsonify({'error': 'API key generation failed'}), 500


# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Serve the main web interface"""
    return send_from_directory('static', 'index.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check if agent is initialized
        if agent is None or agent.connector is None:
            return jsonify({
                'status': 'unhealthy',
                'message': 'Agent not initialized',
                'timestamp': datetime.utcnow().isoformat()
            }), 503
        
        # Check database connection
        node_count = agent.connector.get_node_count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'nodes': node_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@app.route('/api/query', methods=['POST'])
@rate_limit
@validate_input
def query():
    """
    Process a natural language query through the agent
    
    Request body:
    {
        "query": "Is diabetes covered at Apollo Bangalore?",
        "customer_id": "CUST0001",  # Optional
        "session_id": "session_abc123"  # Optional, for conversation memory
    }
    
    Security: Rate limited, input validated
    """
    try:
        # Validate request
        if not request.json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        # Get validated and sanitized inputs (already done by @validate_input)
        user_query = (request.json.get('query') or '').strip()
        customer_id = (request.json.get('customer_id') or '').strip() or None
        session_id = (request.json.get('session_id') or '').strip() or None
        
        if not user_query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Generate session_id if not provided
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:16]}"
        
        # Initialize agent if needed
        if agent is None:
            if not initialize_agent():
                return jsonify({'error': 'Agent initialization failed'}), 503
        
        # Process query with session support
        logger.info(f"Processing query: {user_query[:50]}... (customer: {customer_id}, session: {session_id})")
        response = agent.process_query(user_query, customer_id, session_id)
        
        return jsonify({
            'query': user_query,
            'customer_id': customer_id,
            'session_id': session_id,
            'response': response,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/stats', methods=['GET'])
def statistics():
    """Get database statistics"""
    try:
        if agent is None or agent.connector is None:
            if not initialize_agent():
                return jsonify({'error': 'Agent not initialized'}), 503
        
        # Get node counts by type
        stats = {
            'total_nodes': agent.connector.get_node_count(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Get counts by node type
        node_types = ['Customer', 'Policy', 'Hospital', 'Treatment', 'Medication', 'Claim']
        for node_type in node_types:
            query = f"MATCH (n:{node_type}) RETURN count(n) as count"
            result = agent.connector.execute_query(query)
            stats[f'{node_type.lower()}_count'] = result[0]['count'] if result else 0
        
        # Get relationship count
        rel_query = "MATCH ()-[r]->() RETURN count(r) as count"
        rel_result = agent.connector.execute_query(rel_query)
        stats['total_relationships'] = rel_result[0]['count'] if rel_result else 0
        
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({
            'error': 'Failed to get statistics',
            'message': str(e)
        }), 500


@app.route('/api/customers', methods=['GET'])
def list_customers():
    """List all customers (for demo purposes)"""
    try:
        if agent is None or agent.connector is None:
            if not initialize_agent():
                return jsonify({'error': 'Agent not initialized'}), 503
        
        query = """
        MATCH (c:Customer)
        RETURN c.id as id, c.name as name, c.city as city, c.age as age
        ORDER BY c.id
        LIMIT 20
        """
        
        customers = agent.connector.execute_query(query)
        
        return jsonify({
            'customers': customers,
            'count': len(customers),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error listing customers: {e}")
        return jsonify({
            'error': 'Failed to list customers',
            'message': str(e)
        }), 500


@app.route('/api/schema', methods=['GET'])
def get_schema():
    """Get knowledge graph schema information"""
    try:
        from schema import get_schema_info
        
        schema_info = get_schema_info()
        
        return jsonify({
            'schema': schema_info,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        return jsonify({
            'error': 'Failed to get schema',
            'message': str(e)
        }), 500


@app.route('/api/conversation/<session_id>', methods=['GET'])
def get_conversation_history(session_id):
    """
    Get conversation history for a session
    
    Path parameters:
        session_id: Session identifier
        
    Query parameters:
        last_n: Number of recent messages to return (default: all)
    """
    try:
        if agent is None or agent.memory is None:
            return jsonify({
                'error': 'Conversation memory not available',
                'history': []
            }), 200
        
        last_n = request.args.get('last_n', type=int)
        history = agent.memory.get_history(session_id, last_n)
        metadata = agent.memory.get_session_metadata(session_id)
        
        return jsonify({
            'session_id': session_id,
            'history': history,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return jsonify({
            'error': 'Failed to get conversation history',
            'message': str(e)
        }), 500


@app.route('/api/conversation/<session_id>', methods=['DELETE'])
def clear_conversation(session_id):
    """Clear a conversation session"""
    try:
        if agent is None or agent.memory is None:
            return jsonify({'error': 'Conversation memory not available'}), 503
        
        success = agent.memory.clear_session(session_id)
        
        if success:
            return jsonify({
                'message': f'Session {session_id} cleared successfully',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': 'Session not found',
                'session_id': session_id
            }), 404
    
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        return jsonify({
            'error': 'Failed to clear conversation',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


def shutdown_agent():
    """Cleanup on shutdown"""
    global agent
    if agent:
        logger.info("Closing agent connection...")
        agent.close()
        agent = None


# Register cleanup
import atexit
atexit.register(shutdown_agent)


if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║       🌐 MedAssist Web API - Healthcare Insurance Agent          ║
║                  Powered by Flask + LangGraph                    ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

🚀 Starting server...

📚 Available Endpoints:
  • GET  /                - Web interface
  • GET  /health          - Health check
  • POST /api/query       - Process natural language query
  • GET  /api/stats       - Database statistics
  • GET  /api/customers   - List customers
  • GET  /api/schema      - Get KG schema

📖 API Documentation:
  POST /api/query
  Body: {
    "query": "Is diabetes covered at Apollo?",
    "customer_id": "CUST0001"
  }

🔗 Access the web interface at: http://localhost:5000
""")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Set to True for development
        threaded=True
    )
