"""
Pytest configuration and fixtures for MedAssist testing.
Provides reusable test fixtures for database connections, mocks, and test data.
"""

import pytest
import os
from unittest.mock import Mock, MagicMock
from typing import Generator

# Import core modules
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from neo4j_connector import Neo4jConnector
from vector_store import PolicyVectorStore
from conversation_memory import ConversationMemory
from config import Config


@pytest.fixture(scope="session")
def test_config():
    """
    Provides test configuration.
    Uses environment variables or defaults for testing.
    """
    return {
        "neo4j_uri": os.getenv("NEO4J_URI", "neo4j+s://9ab402cc.databases.neo4j.io"),
        "neo4j_username": os.getenv("NEO4J_USERNAME", "neo4j"),
        "neo4j_password": os.getenv("NEO4J_PASSWORD", ""),
        "gemini_api_key": os.getenv("GOOGLE_API_KEY", ""),
        "environment": "test",
        "log_level": "DEBUG"
    }


@pytest.fixture
def mock_neo4j_connector():
    """
    Provides a mocked Neo4j connector for testing without database calls.
    """
    mock = Mock(spec=Neo4jConnector)
    
    # Mock hospital query response
    mock.execute_query.return_value = [
        {
            "name": "Apollo Hospital",
            "city": "Bangalore",
            "discount": 15,
            "specialties": ["Cardiology", "Neurology"]
        },
        {
            "name": "Fortis Hospital",
            "city": "Bangalore",
            "discount": 10,
            "specialties": ["Oncology", "Orthopedics"]
        }
    ]
    
    return mock


@pytest.fixture
def mock_vector_store():
    """
    Provides a mocked PolicyVectorStore for testing RAG without ChromaDB.
    """
    mock = Mock(spec=PolicyVectorStore)
    
    # Mock RAG search response
    mock.search.return_value = [
        {
            "content": "The comprehensive health policy covers diabetes treatment with a 30-day waiting period.",
            "metadata": {"source": "comprehensive_health_policy.txt"},
            "similarity": 0.92
        },
        {
            "content": "Diabetes-related complications including neuropathy are covered after initial waiting period.",
            "metadata": {"source": "comprehensive_health_policy.txt"},
            "similarity": 0.88
        }
    ]
    
    return mock


@pytest.fixture
def mock_conversation_memory():
    """
    Provides a mocked ConversationMemory for testing without Redis/PostgreSQL.
    """
    mock = Mock(spec=ConversationMemory)
    
    # Mock conversation history
    mock.get_conversation_history.return_value = [
        {"role": "user", "content": "What is covered under my policy?"},
        {"role": "assistant", "content": "The policy covers hospitalization, surgeries, and pre/post hospitalization."}
    ]
    
    mock.add_message.return_value = None
    mock.clear_session.return_value = None
    
    return mock


@pytest.fixture
def mock_gemini_client():
    """
    Provides a mocked Gemini API client for testing LLM calls.
    """
    mock = MagicMock()
    
    # Mock generate_content response
    mock_response = MagicMock()
    mock_response.text = "This is a mocked LLM response for testing."
    mock.generate_content.return_value = mock_response
    
    return mock


@pytest.fixture
def sample_queries():
    """
    Provides sample queries for testing different intents.
    """
    return {
        "hospital_finder": "Show me hospitals in Bangalore with diabetes coverage",
        "coverage_check": "Is diabetes covered in my policy?",
        "policy_utilization": "What is the claim process for hospitalization?",
        "waiting_period": "What are the waiting periods?",
        "exclusions": "What is not covered?",
        "escalation": "I want to speak to a human agent",
        "hybrid": "Show me hospitals in Mumbai with cancer treatment and tell me about cancer coverage"
    }


@pytest.fixture
def sample_kg_results():
    """
    Provides sample Knowledge Graph query results.
    """
    return [
        {
            "name": "Apollo Hospital",
            "city": "Mumbai",
            "discount": 20,
            "specialties": ["Oncology", "Cardiology"],
            "address": "123 Main St, Mumbai",
            "cashless": True
        },
        {
            "name": "Fortis Hospital",
            "city": "Mumbai",
            "discount": 15,
            "specialties": ["Orthopedics", "Neurology"],
            "address": "456 Park Ave, Mumbai",
            "cashless": True
        }
    ]


@pytest.fixture
def sample_rag_results():
    """
    Provides sample RAG search results.
    """
    return [
        {
            "content": "Cancer treatment is covered under the comprehensive policy with a 90-day waiting period.",
            "metadata": {"source": "comprehensive_health_policy.txt", "page": 5},
            "similarity": 0.95
        },
        {
            "content": "Chemotherapy and radiation therapy are included in cancer coverage.",
            "metadata": {"source": "comprehensive_health_policy.txt", "page": 6},
            "similarity": 0.89
        }
    ]


@pytest.fixture
def real_neo4j_connector(test_config):
    """
    Provides a real Neo4j connector for integration tests.
    Only use when NEO4J credentials are available.
    """
    if not test_config["neo4j_password"]:
        pytest.skip("Neo4j credentials not available for integration test")
    
    connector = Neo4jConnector(
        uri=test_config["neo4j_uri"],
        username=test_config["neo4j_username"],
        password=test_config["neo4j_password"]
    )
    
    yield connector
    
    connector.close()


@pytest.fixture
def real_vector_store():
    """
    Provides a real PolicyVectorStore for integration tests.
    Uses the actual ChromaDB instance.
    """
    vector_store = PolicyVectorStore(persist_directory="./chroma_db")
    
    yield vector_store
    
    # Cleanup not needed as we use persistent DB


@pytest.fixture(autouse=True)
def reset_environment():
    """
    Automatically resets environment between tests.
    """
    # Store original environment
    original_env = os.environ.copy()
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_agent_state():
    """
    Provides a sample AgentState for testing LangGraph nodes.
    """
    return {
        "user_query": "Show me hospitals in Bangalore",
        "conversation_history": [],
        "classified_intent": "hospital_finder",
        "confidence": 0.92,
        "kg_results": [],
        "rag_context": [],
        "response": "",
        "needs_escalation": False,
        "needs_hybrid": False,
        "session_id": "test-session-123"
    }


@pytest.fixture
def captured_logs(caplog):
    """
    Provides captured logs for testing logging behavior.
    """
    return caplog


# Test markers for different test categories
def pytest_configure(config):
    """
    Register custom markers for test categorization.
    """
    config.addinivalue_line("markers", "unit: Unit tests that don't require external services")
    config.addinivalue_line("markers", "integration: Integration tests that require Neo4j/ChromaDB")
    config.addinivalue_line("markers", "slow: Slow tests that take significant time")
    config.addinivalue_line("markers", "api: Tests for web API endpoints")
