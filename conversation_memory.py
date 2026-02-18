"""
Conversation Memory Management for Multi-turn Conversations
Tracks conversation history and provides context for follow-up questions
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manages conversation history for multi-turn interactions"""
    
    def __init__(self, max_history: int = 10, ttl_minutes: int = 60, persist_dir: str = "./conversation_history"):
        """
        Initialize conversation memory
        
        Args:
            max_history: Maximum number of messages to keep per conversation
            ttl_minutes: Time-to-live for conversations in minutes
            persist_dir: Directory to persist conversation history
        """
        self.max_history = max_history
        self.ttl_minutes = ttl_minutes
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)
        
        # In-memory storage: {session_id: conversation_data}
        self.conversations = {}
        self.lock = threading.Lock()
        
        logger.info(f"✓ Conversation memory initialized (max_history={max_history}, ttl={ttl_minutes}min)")
    
    def create_session(self, session_id: str, customer_id: Optional[str] = None) -> Dict:
        """
        Create a new conversation session
        
        Args:
            session_id: Unique session identifier
            customer_id: Optional customer ID
            
        Returns:
            Session metadata
        """
        with self.lock:
            session_data = {
                'session_id': session_id,
                'customer_id': customer_id,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'messages': [],
                'metadata': {}
            }
            self.conversations[session_id] = session_data
            logger.info(f"Created session: {session_id} (customer: {customer_id})")
            return session_data
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a message to conversation history
        
        Args:
            session_id: Session identifier
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata (intent, confidence, etc.)
        """
        with self.lock:
            if session_id not in self.conversations:
                logger.warning(f"Session {session_id} not found, creating new session")
                self.create_session(session_id)
            
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            self.conversations[session_id]['messages'].append(message)
            self.conversations[session_id]['last_accessed'] = datetime.now().isoformat()
            
            # Trim history if needed
            if len(self.conversations[session_id]['messages']) > self.max_history:
                self.conversations[session_id]['messages'] = \
                    self.conversations[session_id]['messages'][-self.max_history:]
            
            logger.debug(f"Added {role} message to session {session_id}")
    
    def get_history(self, session_id: str, last_n: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            last_n: Number of recent messages to return (None for all)
            
        Returns:
            List of messages
        """
        with self.lock:
            if session_id not in self.conversations:
                logger.warning(f"Session {session_id} not found")
                return []
            
            self.conversations[session_id]['last_accessed'] = datetime.now().isoformat()
            messages = self.conversations[session_id]['messages']
            
            if last_n:
                return messages[-last_n:]
            return messages
    
    def get_context_string(self, session_id: str, last_n: int = 5) -> str:
        """
        Get formatted conversation history as a string for context
        
        Args:
            session_id: Session identifier
            last_n: Number of recent messages to include
            
        Returns:
            Formatted conversation history
        """
        history = self.get_history(session_id, last_n)
        
        if not history:
            return ""
        
        context_parts = []
        for msg in history:
            role = msg['role'].capitalize()
            content = msg['content']
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def get_session_metadata(self, session_id: str) -> Optional[Dict]:
        """Get session metadata"""
        with self.lock:
            if session_id not in self.conversations:
                return None
            return {
                'session_id': session_id,
                'customer_id': self.conversations[session_id].get('customer_id'),
                'created_at': self.conversations[session_id]['created_at'],
                'last_accessed': self.conversations[session_id]['last_accessed'],
                'message_count': len(self.conversations[session_id]['messages'])
            }
    
    def update_customer_id(self, session_id: str, customer_id: str):
        """Update customer ID for a session"""
        with self.lock:
            if session_id in self.conversations:
                self.conversations[session_id]['customer_id'] = customer_id
                logger.info(f"Updated customer_id for session {session_id}: {customer_id}")
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear a conversation session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was cleared, False if not found
        """
        with self.lock:
            if session_id in self.conversations:
                del self.conversations[session_id]
                logger.info(f"Cleared session: {session_id}")
                return True
            return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions based on TTL"""
        with self.lock:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, data in self.conversations.items():
                last_accessed = datetime.fromisoformat(data['last_accessed'])
                if current_time - last_accessed > timedelta(minutes=self.ttl_minutes):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                # Optionally persist before deleting
                self._persist_session(session_id)
                del self.conversations[session_id]
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
            return len(expired_sessions)
    
    def _persist_session(self, session_id: str):
        """Persist a session to disk"""
        try:
            if session_id in self.conversations:
                file_path = self.persist_dir / f"{session_id}.json"
                with open(file_path, 'w') as f:
                    json.dump(self.conversations[session_id], f, indent=2)
                logger.debug(f"Persisted session {session_id}")
        except Exception as e:
            logger.error(f"Error persisting session {session_id}: {e}")
    
    def load_session(self, session_id: str) -> bool:
        """
        Load a session from disk
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was loaded, False otherwise
        """
        try:
            file_path = self.persist_dir / f"{session_id}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    session_data = json.load(f)
                
                with self.lock:
                    self.conversations[session_id] = session_data
                    self.conversations[session_id]['last_accessed'] = datetime.now().isoformat()
                
                logger.info(f"Loaded session {session_id} from disk")
                return True
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
        
        return False
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        with self.lock:
            return list(self.conversations.keys())
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        with self.lock:
            total_messages = sum(len(conv['messages']) for conv in self.conversations.values())
            
            return {
                'active_sessions': len(self.conversations),
                'total_messages': total_messages,
                'persist_directory': str(self.persist_dir),
                'max_history_per_session': self.max_history,
                'ttl_minutes': self.ttl_minutes
            }


if __name__ == "__main__":
    # Test the conversation memory
    logging.basicConfig(level=logging.INFO)
    
    memory = ConversationMemory(max_history=5, ttl_minutes=30)
    
    # Create a test session
    session_id = "test_session_001"
    memory.create_session(session_id, customer_id="CUST0001")
    
    # Add some messages
    memory.add_message(session_id, "user", "Is diabetes covered?")
    memory.add_message(session_id, "assistant", "Yes, diabetes is covered after a 2-year waiting period.")
    memory.add_message(session_id, "user", "What about cancer?")
    memory.add_message(session_id, "assistant", "Cancer is fully covered including chemotherapy and radiation.")
    
    # Get context
    print("\n=== Conversation Context ===")
    print(memory.get_context_string(session_id))
    
    print("\n=== Session Metadata ===")
    print(json.dumps(memory.get_session_metadata(session_id), indent=2))
    
    print("\n=== Memory Stats ===")
    print(json.dumps(memory.get_stats(), indent=2))
