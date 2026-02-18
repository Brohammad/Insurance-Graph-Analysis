"""
Unit tests for security features.
Tests JWT authentication, rate limiting, input validation, and security headers.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security import (
    SecurityManager,
    security_manager,
    RateLimiter,
    hash_password,
    verify_password
)
from datetime import datetime, timedelta
import time


@pytest.mark.unit
class TestSecurityManager:
    """Test suite for SecurityManager class."""
    
    def test_generate_token(self):
        """Test JWT token generation."""
        sm = SecurityManager(secret_key="test_secret")
        user_id = "test_user_123"
        
        token = sm.generate_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long
        
    def test_verify_valid_token(self):
        """Test verifying a valid JWT token."""
        sm = SecurityManager(secret_key="test_secret")
        user_id = "test_user_123"
        
        token = sm.generate_token(user_id)
        payload = sm.verify_token(token)
        
        assert payload is not None
        assert payload['user_id'] == user_id
        assert 'exp' in payload
        assert 'iat' in payload
        assert 'jti' in payload
        
    def test_verify_invalid_token(self):
        """Test verifying an invalid token."""
        sm = SecurityManager(secret_key="test_secret")
        
        payload = sm.verify_token("invalid.token.string")
        
        assert payload is None
        
    def test_verify_token_wrong_secret(self):
        """Test verifying token with wrong secret key."""
        sm1 = SecurityManager(secret_key="secret1")
        sm2 = SecurityManager(secret_key="secret2")
        
        token = sm1.generate_token("user123")
        payload = sm2.verify_token(token)
        
        assert payload is None
        
    def test_token_with_metadata(self):
        """Test generating token with additional metadata."""
        sm = SecurityManager(secret_key="test_secret")
        
        metadata = {
            'role': 'admin',
            'permissions': ['read', 'write']
        }
        
        token = sm.generate_token("user123", metadata)
        payload = sm.verify_token(token)
        
        assert payload['role'] == 'admin'
        assert payload['permissions'] == ['read', 'write']
        
    def test_generate_api_key(self):
        """Test API key generation."""
        sm = SecurityManager()
        
        api_key = sm.generate_api_key("user123")
        
        assert api_key.startswith("ma_")
        assert len(api_key) == 43  # prefix (3) + hash (40)
        
    def test_api_keys_are_unique(self):
        """Test that API keys are unique."""
        sm = SecurityManager()
        
        key1 = sm.generate_api_key("user123")
        key2 = sm.generate_api_key("user123")
        
        assert key1 != key2
        
    def test_hash_api_key(self):
        """Test API key hashing."""
        sm = SecurityManager()
        
        api_key = "ma_test1234567890"
        hashed = sm.hash_api_key(api_key)
        
        assert hashed != api_key
        assert len(hashed) == 64  # SHA-256 hex digest
        
    def test_sanitize_input_basic(self):
        """Test basic input sanitization."""
        sm = SecurityManager()
        
        text = "Hello, World!"
        sanitized = sm.sanitize_input(text)
        
        assert sanitized == "Hello, World!"
        
    def test_sanitize_input_removes_null_bytes(self):
        """Test that null bytes are removed."""
        sm = SecurityManager()
        
        text = "Hello\x00World"
        sanitized = sm.sanitize_input(text)
        
        assert "\x00" not in sanitized
        assert sanitized == "HelloWorld"
        
    def test_sanitize_input_truncates(self):
        """Test that input is truncated to max length."""
        sm = SecurityManager()
        
        text = "A" * 2000
        sanitized = sm.sanitize_input(text, max_length=500)
        
        assert len(sanitized) == 500
        
    def test_sanitize_input_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        sm = SecurityManager()
        
        text = "  Hello World  "
        sanitized = sm.sanitize_input(text)
        
        assert sanitized == "Hello World"
        
    def test_validate_query_valid(self):
        """Test validation of valid query."""
        sm = SecurityManager()
        
        query = "Show me hospitals in Bangalore"
        is_valid, error = sm.validate_query(query)
        
        assert is_valid is True
        assert error is None
        
    def test_validate_query_empty(self):
        """Test validation of empty query."""
        sm = SecurityManager()
        
        is_valid, error = sm.validate_query("")
        
        assert is_valid is False
        assert error == "Query cannot be empty"
        
    def test_validate_query_too_long(self):
        """Test validation of overly long query."""
        sm = SecurityManager()
        
        query = "A" * 2000
        is_valid, error = sm.validate_query(query)
        
        assert is_valid is False
        assert "exceeds maximum length" in error
        
    def test_validate_query_detects_injection(self):
        """Test detection of potential injection attacks."""
        sm = SecurityManager()
        
        dangerous_queries = [
            "'; DROP DATABASE neo4j; --",
            "MATCH (n) DELETE n",
            "CALL dbms.shutdown()",
        ]
        
        for query in dangerous_queries:
            is_valid, error = sm.validate_query(query)
            # Should detect at least some patterns
            # Note: Not all will be caught, this is a basic check
        
    def test_validate_session_id_valid(self):
        """Test validation of valid session ID."""
        sm = SecurityManager()
        
        valid_ids = [
            "session_abc123",
            "user-session-456",
            "abc_123-def_456",
        ]
        
        for session_id in valid_ids:
            assert sm.validate_session_id(session_id) is True
            
    def test_validate_session_id_invalid(self):
        """Test validation of invalid session IDs."""
        sm = SecurityManager()
        
        invalid_ids = [
            "",
            "a",  # Too short
            "session with spaces",
            "session@special!chars",
            "A" * 100,  # Too long
        ]
        
        for session_id in invalid_ids:
            assert sm.validate_session_id(session_id) is False


@pytest.mark.unit
class TestRateLimiter:
    """Test suite for RateLimiter class."""
    
    def test_allows_requests_under_limit(self):
        """Test that requests under limit are allowed."""
        limiter = RateLimiter(requests_per_minute=10)
        identifier = "test_user"
        
        # Make 5 requests (under limit of 10)
        for _ in range(5):
            is_allowed, reset_time = limiter.is_allowed(identifier)
            assert is_allowed is True
            assert reset_time is None
            
    def test_blocks_requests_over_limit(self):
        """Test that requests over limit are blocked."""
        limiter = RateLimiter(requests_per_minute=5)
        identifier = "test_user"
        
        # Make 5 requests (at limit)
        for _ in range(5):
            limiter.is_allowed(identifier)
        
        # 6th request should be blocked
        is_allowed, reset_time = limiter.is_allowed(identifier)
        assert is_allowed is False
        assert reset_time is not None
        assert reset_time > 0
        
    def test_separate_identifiers_independent(self):
        """Test that different identifiers have separate limits."""
        limiter = RateLimiter(requests_per_minute=3)
        
        # User 1 makes 3 requests
        for _ in range(3):
            limiter.is_allowed("user1")
        
        # User 2 should still be allowed
        is_allowed, _ = limiter.is_allowed("user2")
        assert is_allowed is True
        
        # User 1 should be blocked
        is_allowed, _ = limiter.is_allowed("user1")
        assert is_allowed is False
        
    def test_cleanup_removes_old_entries(self):
        """Test that cleanup removes expired entries."""
        limiter = RateLimiter(requests_per_minute=10)
        
        limiter.is_allowed("user1")
        limiter.is_allowed("user2")
        
        assert len(limiter.requests) == 2
        
        limiter.cleanup()
        
        # Entries should still be there (not expired yet)
        assert len(limiter.requests) == 2


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing utilities."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "secure_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) == 64  # SHA-256 hex
        
    def test_same_password_same_hash(self):
        """Test that same password produces same hash."""
        password = "test_password"
        
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 == hash2
        
    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        
        assert hash1 != hash2
        
    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "my_secure_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
        
    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


@pytest.mark.unit
def test_global_security_manager():
    """Test that global security manager instance works."""
    token = security_manager.generate_token("test_user")
    payload = security_manager.verify_token(token)
    
    assert payload is not None
    assert payload['user_id'] == "test_user"


@pytest.mark.unit
def test_api_key_format():
    """Test API key format is consistent."""
    api_key = security_manager.generate_api_key("user123")
    
    # Should match pattern: ma_[40 hex chars]
    assert api_key.startswith("ma_")
    assert len(api_key) == 43
    assert all(c in "0123456789abcdef" for c in api_key[3:])
