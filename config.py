"""
Production configuration for MedAssist.
Handles environment-specific settings with secure defaults.
"""
import os
from typing import Optional, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Application configuration with environment variable support."""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Neo4j Configuration
    NEO4J_URI: str = os.getenv("NEO4J_URI", "neo4j+s://9ab402cc.databases.neo4j.io")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")
    
    # Gemini API Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    # LLM Configuration
    LLM_MODEL: str = "gemini-2.0-flash"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 2048
    
    # Agent Configuration
    CONFIDENCE_THRESHOLD: float = 0.7
    MAX_RETRIES: int = 3
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
    
    # PostgreSQL Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://medassist:medassist123@localhost:5432/medassist"
    )
    
    # Vector Store Configuration
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Conversation Memory Settings
    MAX_CONVERSATION_MESSAGES: int = int(os.getenv("MAX_CONVERSATION_MESSAGES", "10"))
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "5000"))
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Sentry Configuration (for error tracking)
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    
    # CORS Settings - use field with default_factory for mutable types
    CORS_ORIGINS: List[str] = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(","))
    
    # Gunicorn Settings (for production)
    GUNICORN_WORKERS: int = int(os.getenv("GUNICORN_WORKERS", "4"))
    GUNICORN_TIMEOUT: int = int(os.getenv("GUNICORN_TIMEOUT", "120"))
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validates that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid, raises ValueError otherwise
        """
        config = cls()
        errors = []
        
        # Check required credentials
        if not config.NEO4J_PASSWORD:
            errors.append("NEO4J_PASSWORD is required")
        
        if not config.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is required")
        
        if config.ENVIRONMENT == "production":
            if config.SECRET_KEY == "dev-secret-key-change-in-production":
                errors.append("SECRET_KEY must be changed in production")
            
            if not config.SENTRY_DSN:
                errors.append("SENTRY_DSN is recommended for production")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(errors))
        
        return True
    
    @classmethod
    def get_database_config(cls):
        """Returns database configuration dictionary."""
        config = cls()
        return {
            "neo4j": {
                "uri": config.NEO4J_URI,
                "username": config.NEO4J_USERNAME,
                "password": config.NEO4J_PASSWORD,
            },
            "postgres": {
                "url": config.DATABASE_URL,
            },
            "redis": {
                "url": config.REDIS_URL,
                "max_connections": config.REDIS_MAX_CONNECTIONS,
            },
        }
    
    @classmethod
    def get_llm_config(cls):
        """Returns LLM configuration dictionary."""
        config = cls()
        return {
            "api_key": config.GOOGLE_API_KEY,
            "model": config.GEMINI_MODEL,
        }
    
    @classmethod
    def get_logging_config(cls):
        """Returns logging configuration dictionary."""
        config = cls()
        return {
            "level": config.LOG_LEVEL,
            "format": config.LOG_FORMAT,
            "sentry_dsn": config.SENTRY_DSN,
            "traces_sample_rate": config.SENTRY_TRACES_SAMPLE_RATE,
        }
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls().ENVIRONMENT == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment."""
        return cls().ENVIRONMENT == "development"
    
    @classmethod
    def is_test(cls) -> bool:
        """Check if running in test environment."""
        return cls().ENVIRONMENT == "test"


# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    RATE_LIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    LOG_LEVEL = "INFO"
    RATE_LIMIT_ENABLED = True


class TestConfig(Config):
    """Test-specific configuration."""
    ENVIRONMENT = "test"
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DATABASE_URL = "sqlite:///:memory:"
    REDIS_URL = "redis://localhost:6379/15"  # Different Redis DB for testing


def get_config() -> Config:
    """
    Factory function to get appropriate config based on environment.
    
    Returns:
        Config: Configuration instance for current environment
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "test": TestConfig,
    }
    
    return config_map.get(env, Config)()


# Create a singleton instance
config = get_config()

# Legacy exports for backward compatibility
NEO4J_URI = config.NEO4J_URI
NEO4J_USERNAME = config.NEO4J_USERNAME
NEO4J_PASSWORD = config.NEO4J_PASSWORD
NEO4J_DATABASE = config.NEO4J_DATABASE
GOOGLE_API_KEY = config.GOOGLE_API_KEY
LLM_MODEL = config.LLM_MODEL
LLM_TEMPERATURE = config.LLM_TEMPERATURE
LLM_MAX_TOKENS = config.LLM_MAX_TOKENS
CONFIDENCE_THRESHOLD = config.CONFIDENCE_THRESHOLD
MAX_RETRIES = config.MAX_RETRIES


def validate_config():
    """Validate that all required configuration is present (legacy wrapper)"""
    return Config.validate()


if __name__ == "__main__":
    try:
        Config.validate()
        print("✓ Configuration validation passed")
        print(f"  Environment: {config.ENVIRONMENT}")
        print(f"  Debug: {config.DEBUG}")
        print(f"  Neo4j URI: {config.NEO4J_URI}")
        print(f"  Neo4j Database: {config.NEO4J_DATABASE}")
        print(f"  LLM Model: {config.LLM_MODEL}")
        print(f"  Rate limiting: {config.RATE_LIMIT_ENABLED}")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
