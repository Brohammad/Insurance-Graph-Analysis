"""
Security middleware and utilities for MedAssist API.
Includes JWT authentication, rate limiting, input validation, and security headers.
"""

from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta
import jwt
import re
import hashlib
import secrets
from typing import Optional, Dict, Any
import logging

from config import config

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages security features including JWT, rate limiting, and validation."""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or config.SECRET_KEY
        self.jwt_expiration_hours = config.JWT_EXPIRATION_HOURS
        
    def generate_token(self, user_id: str, metadata: Dict[str, Any] = None) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user_id: Unique user identifier
            metadata: Additional claims to include in token
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)  # JWT ID for token revocation
        }
        
        if metadata:
            payload.update(metadata)
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def generate_api_key(self, user_id: str) -> str:
        """
        Generate a secure API key for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            API key string
        """
        # Format: prefix_random_hash
        random_bytes = secrets.token_bytes(32)
        user_bytes = user_id.encode('utf-8')
        
        combined = random_bytes + user_bytes
        api_key_hash = hashlib.sha256(combined).hexdigest()
        
        return f"ma_{api_key_hash[:40]}"
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(api_key.encode('utf-8')).hexdigest()
    
    def sanitize_input(self, text: str, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Truncate to max length
        text = text[:max_length]
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def validate_query(self, query: str) -> tuple[bool, Optional[str]]:
        """
        Validate a user query for security issues.
        
        Args:
            query: User query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Query cannot be empty"
        
        if len(query) > 1000:
            return False, "Query exceeds maximum length (1000 characters)"
        
        # Check for potential Cypher injection patterns
        dangerous_patterns = [
            r'(?i)\bDROP\s+DATABASE\b',
            r'(?i)\bDELETE\s+.*\bDETACH\b',
            r'(?i)\bCREATE\s+.*\bCONSTRAINT\b',
            r'(?i)\bCALL\s+dbms\.',
            r';\s*DROP\s+',
            r'--\s*$',  # SQL-style comments
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query):
                logger.warning(f"Potentially dangerous query pattern detected: {pattern}")
                return False, "Query contains invalid patterns"
        
        return True, None
    
    def validate_session_id(self, session_id: str) -> bool:
        """Validate session ID format."""
        if not session_id:
            return False
        
        # Session ID should be alphanumeric + hyphens/underscores, reasonable length
        pattern = r'^[a-zA-Z0-9_-]{8,64}$'
        return bool(re.match(pattern, session_id))


# Global security manager instance
security_manager = SecurityManager()


def require_auth(f):
    """
    Decorator to require JWT authentication for a route.
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            user_id = g.user_id
            return jsonify({'message': f'Hello {user_id}'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Also check query parameter (less secure, but useful for development)
        if not token:
            token = request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Missing authentication token'}), 401
        
        # Verify token
        payload = security_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Store user info in request context
        g.user_id = payload.get('user_id')
        g.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated


def require_api_key(f):
    """
    Decorator to require API key authentication for a route.
    
    Usage:
        @app.route('/api/query')
        @require_api_key
        def api_query():
            return jsonify({'data': 'protected'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = None
        
        # Check for API key in header
        api_key = request.headers.get('X-API-Key')
        
        # Also check query parameter
        if not api_key:
            api_key = request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'Missing API key'}), 401
        
        # Validate API key format
        if not api_key.startswith('ma_') or len(api_key) != 43:
            return jsonify({'error': 'Invalid API key format'}), 401
        
        # TODO: Verify API key against database
        # For now, we'll accept properly formatted keys in development
        if config.ENVIRONMENT == 'production':
            # In production, you'd verify against database:
            # if not verify_api_key_in_db(api_key):
            #     return jsonify({'error': 'Invalid API key'}), 401
            pass
        
        return f(*args, **kwargs)
    
    return decorated


def validate_input(f):
    """
    Decorator to validate and sanitize request input.
    
    Usage:
        @app.route('/query', methods=['POST'])
        @validate_input
        def query():
            data = request.get_json()
            # data['query'] is now sanitized
            return jsonify({'status': 'ok'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Sanitize query if present
            if 'query' in data:
                data['query'] = security_manager.sanitize_input(data['query'])
                
                # Validate query
                is_valid, error = security_manager.validate_query(data['query'])
                if not is_valid:
                    return jsonify({'error': error}), 400
            
            # Sanitize session_id if present
            if 'session_id' in data:
                if not security_manager.validate_session_id(data['session_id']):
                    return jsonify({'error': 'Invalid session ID format'}), 400
            
            # Sanitize customer_id if present
            if 'customer_id' in data:
                data['customer_id'] = security_manager.sanitize_input(
                    data['customer_id'], 
                    max_length=100
                )
        
        return f(*args, **kwargs)
    
    return decorated


def add_security_headers(response):
    """
    Add security headers to response.
    
    Usage in Flask:
        @app.after_request
        def apply_security_headers(response):
            return add_security_headers(response)
    """
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # HTTPS only (if in production)
    if config.ENVIRONMENT == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:;"
    )
    
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # {ip: [(timestamp, count)]}
    
    def is_allowed(self, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            identifier: IP address or user ID
            
        Returns:
            Tuple of (is_allowed, seconds_until_reset)
        """
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                (ts, count) for ts, count in self.requests[identifier]
                if ts > minute_ago
            ]
        
        # Count requests in last minute
        current_count = sum(
            count for ts, count in self.requests.get(identifier, [])
        )
        
        if current_count >= self.requests_per_minute:
            # Calculate seconds until oldest request expires
            if self.requests[identifier]:
                oldest_ts = min(ts for ts, _ in self.requests[identifier])
                reset_time = (oldest_ts + timedelta(minutes=1) - now).total_seconds()
                return False, max(1, int(reset_time))
            return False, 60
        
        # Add new request
        if identifier not in self.requests:
            self.requests[identifier] = []
        self.requests[identifier].append((now, 1))
        
        return True, None
    
    def cleanup(self):
        """Remove expired entries."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                (ts, count) for ts, count in self.requests[identifier]
                if ts > minute_ago
            ]
            
            if not self.requests[identifier]:
                del self.requests[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=config.RATE_LIMIT_PER_MINUTE)


def rate_limit(f):
    """
    Decorator to apply rate limiting to a route.
    
    Usage:
        @app.route('/api/query')
        @rate_limit
        def query():
            return jsonify({'data': 'result'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not config.RATE_LIMIT_ENABLED:
            return f(*args, **kwargs)
        
        # Use user_id if authenticated, otherwise use IP
        identifier = getattr(g, 'user_id', None) or request.remote_addr
        
        is_allowed, reset_time = rate_limiter.is_allowed(identifier)
        
        if not is_allowed:
            response = jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': reset_time
            })
            response.headers['Retry-After'] = str(reset_time)
            return response, 429
        
        return f(*args, **kwargs)
    
    return decorated


# Utility functions for password hashing (if implementing user auth)
def hash_password(password: str) -> str:
    """Hash a password using SHA-256 (use bcrypt in production)."""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == hashed
