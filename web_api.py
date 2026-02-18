"""
MedAssist Web API - Flask REST API for Healthcare Insurance Agent
Provides HTTP endpoints for the LangGraph agent
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from agent import MedAssistAgent
from neo4j_connector import Neo4jConnector
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Global agent instance
agent = None
connector = None


def initialize_agent():
    """Initialize the agent and database connection"""
    global agent, connector
    try:
        agent = MedAssistAgent()
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
def query():
    """
    Process a natural language query through the agent
    
    Request body:
    {
        "query": "Is diabetes covered at Apollo Bangalore?",
        "customer_id": "CUST0001"  # Optional
    }
    """
    try:
        # Validate request
        if not request.json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        user_query = request.json.get('query', '').strip()
        customer_id = request.json.get('customer_id', '').strip() or None
        
        if not user_query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Initialize agent if needed
        if agent is None:
            if not initialize_agent():
                return jsonify({'error': 'Agent initialization failed'}), 503
        
        # Process query
        logger.info(f"Processing query: {user_query} (customer: {customer_id})")
        response = agent.process_query(user_query, customer_id)
        
        return jsonify({
            'query': user_query,
            'customer_id': customer_id,
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
