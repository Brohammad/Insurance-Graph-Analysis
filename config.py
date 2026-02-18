"""
Configuration module for MedAssist Healthcare Insurance Knowledge Graph
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://9ab402cc.databases.neo4j.io")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Gemini API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# LLM Configuration
LLM_MODEL = "gemini-2.0-flash"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 2048

# Agent Configuration
CONFIDENCE_THRESHOLD = 0.7
MAX_RETRIES = 3

def validate_config():
    """Validate that all required configuration is present"""
    errors = []
    
    if not NEO4J_PASSWORD:
        errors.append("NEO4J_PASSWORD is not set")
    
    if not GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY is not set")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True

if __name__ == "__main__":
    try:
        validate_config()
        print("✓ Configuration validated successfully")
        print(f"  Neo4j URI: {NEO4J_URI}")
        print(f"  Neo4j Database: {NEO4J_DATABASE}")
        print(f"  LLM Model: {LLM_MODEL}")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
