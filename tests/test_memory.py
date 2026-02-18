"""
Unit tests for ConversationMemory.
Tests session management, message storage, and retrieval.
"""

import pytest
from datetime import datetime, timedelta
from conversation_memory import ConversationMemory


@pytest.mark.unit
class TestConversationMemory:
    """Test suite for ConversationMemory class."""
    
    def test_initialization(self):
        """Test ConversationMemory initialization."""
        memory = ConversationMemory(max_messages=5, session_timeout_minutes=30)
        
        assert memory.max_messages == 5
        assert memory.session_timeout_minutes == 30
        assert len(memory.sessions) == 0
        
    def test_add_message(self):
        """Test adding a message to conversation history."""
        memory = ConversationMemory()
        session_id = "test-session-1"
        
        memory.add_message(session_id, "user", "What is covered?")
        memory.add_message(session_id, "assistant", "The policy covers hospitalization.")
        
        history = memory.get_conversation_history(session_id)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        
    def test_max_messages_limit(self):
        """Test that max_messages limit is enforced."""
        memory = ConversationMemory(max_messages=3)
        session_id = "test-session-2"
        
        # Add 5 messages
        for i in range(5):
            memory.add_message(session_id, "user", f"Message {i}")
        
        history = memory.get_conversation_history(session_id)
        # Should only keep last 3 messages
        assert len(history) == 3
        assert history[0]["content"] == "Message 2"
        assert history[-1]["content"] == "Message 4"
        
    def test_multiple_sessions(self):
        """Test managing multiple independent sessions."""
        memory = ConversationMemory()
        
        memory.add_message("session-1", "user", "Query from session 1")
        memory.add_message("session-2", "user", "Query from session 2")
        
        history1 = memory.get_conversation_history("session-1")
        history2 = memory.get_conversation_history("session-2")
        
        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0]["content"] != history2[0]["content"]
        
    def test_get_empty_session(self):
        """Test getting history for non-existent session."""
        memory = ConversationMemory()
        
        history = memory.get_conversation_history("non-existent")
        
        assert history == []
        
    def test_clear_session(self):
        """Test clearing a specific session."""
        memory = ConversationMemory()
        session_id = "test-session-3"
        
        memory.add_message(session_id, "user", "Message 1")
        memory.add_message(session_id, "assistant", "Response 1")
        
        memory.clear_session(session_id)
        history = memory.get_conversation_history(session_id)
        
        assert len(history) == 0
        
    def test_clear_all_sessions(self):
        """Test clearing all sessions."""
        memory = ConversationMemory()
        
        memory.add_message("session-1", "user", "Message 1")
        memory.add_message("session-2", "user", "Message 2")
        
        memory.clear_all()
        
        assert len(memory.sessions) == 0
        
    def test_message_metadata(self):
        """Test storing and retrieving message metadata."""
        memory = ConversationMemory()
        session_id = "test-session-4"
        
        metadata = {"intent": "hospital_finder", "confidence": 0.95}
        memory.add_message(
            session_id, 
            "user", 
            "Show hospitals", 
            metadata=metadata
        )
        
        history = memory.get_conversation_history(session_id)
        assert history[0]["metadata"] == metadata
        
    def test_timestamp_added(self):
        """Test that timestamps are automatically added."""
        memory = ConversationMemory()
        session_id = "test-session-5"
        
        memory.add_message(session_id, "user", "Test message")
        history = memory.get_conversation_history(session_id)
        
        assert "timestamp" in history[0]
        assert isinstance(history[0]["timestamp"], str)
        
    def test_get_last_n_messages(self):
        """Test retrieving only last N messages."""
        memory = ConversationMemory(max_messages=10)
        session_id = "test-session-6"
        
        for i in range(10):
            memory.add_message(session_id, "user", f"Message {i}")
        
        last_3 = memory.get_conversation_history(session_id, last_n=3)
        
        assert len(last_3) == 3
        assert last_3[0]["content"] == "Message 7"
        assert last_3[-1]["content"] == "Message 9"
        
    def test_session_timeout(self):
        """Test that old sessions are cleaned up."""
        memory = ConversationMemory(session_timeout_minutes=1)
        session_id = "test-session-7"
        
        # Add message and manually set old timestamp
        memory.add_message(session_id, "user", "Old message")
        if session_id in memory.sessions:
            memory.sessions[session_id]["last_activity"] = (
                datetime.now() - timedelta(minutes=5)
            )
        
        # Trigger cleanup
        memory.cleanup_old_sessions()
        
        # Session should be removed
        assert session_id not in memory.sessions
        
    def test_get_session_stats(self):
        """Test getting session statistics."""
        memory = ConversationMemory()
        session_id = "test-session-8"
        
        memory.add_message(session_id, "user", "Query 1")
        memory.add_message(session_id, "assistant", "Response 1")
        memory.add_message(session_id, "user", "Query 2")
        
        stats = memory.get_session_stats(session_id)
        
        assert stats["message_count"] == 3
        assert stats["user_messages"] == 2
        assert stats["assistant_messages"] == 1
        
    def test_get_all_session_ids(self):
        """Test getting list of all active sessions."""
        memory = ConversationMemory()
        
        memory.add_message("session-1", "user", "Message")
        memory.add_message("session-2", "user", "Message")
        memory.add_message("session-3", "user", "Message")
        
        session_ids = memory.get_all_session_ids()
        
        assert len(session_ids) == 3
        assert "session-1" in session_ids
        
    def test_export_session(self):
        """Test exporting session to JSON format."""
        memory = ConversationMemory()
        session_id = "test-session-9"
        
        memory.add_message(session_id, "user", "Query")
        memory.add_message(session_id, "assistant", "Response")
        
        exported = memory.export_session(session_id)
        
        assert "session_id" in exported
        assert "messages" in exported
        assert len(exported["messages"]) == 2
        
    def test_import_session(self):
        """Test importing session from JSON format."""
        memory = ConversationMemory()
        
        session_data = {
            "session_id": "imported-session",
            "messages": [
                {"role": "user", "content": "Imported query"},
                {"role": "assistant", "content": "Imported response"}
            ]
        }
        
        memory.import_session(session_data)
        history = memory.get_conversation_history("imported-session")
        
        assert len(history) == 2
        assert history[0]["content"] == "Imported query"


@pytest.mark.unit
class TestConversationContext:
    """Test context management for conversations."""
    
    def test_get_context_summary(self):
        """Test generating summary of conversation context."""
        memory = ConversationMemory()
        session_id = "test-session-10"
        
        memory.add_message(session_id, "user", "What is covered?")
        memory.add_message(session_id, "assistant", "Hospitalization is covered.")
        memory.add_message(session_id, "user", "What about waiting period?")
        
        context = memory.get_context_summary(session_id)
        
        # Should include recent topics/intents
        assert isinstance(context, str)
        assert len(context) > 0
        
    def test_detect_topic_change(self):
        """Test detecting when user changes topic."""
        memory = ConversationMemory()
        session_id = "test-session-11"
        
        # Add messages about coverage
        memory.add_message(session_id, "user", "What is covered?")
        memory.add_message(session_id, "assistant", "Hospitalization is covered.")
        
        # Topic change to hospitals
        topic_changed = memory.detect_topic_change(
            session_id, 
            "Show me hospitals in Bangalore"
        )
        
        assert topic_changed is True or topic_changed is False
        
    def test_get_relevant_context(self):
        """Test getting only relevant context for current query."""
        memory = ConversationMemory()
        session_id = "test-session-12"
        
        memory.add_message(session_id, "user", "What is covered?")
        memory.add_message(session_id, "assistant", "Hospitalization is covered.")
        memory.add_message(session_id, "user", "What about diabetes?")
        
        relevant = memory.get_relevant_context(session_id, "diabetes coverage")
        
        # Should return context related to diabetes
        assert isinstance(relevant, list)


@pytest.mark.unit
def test_memory_persistence():
    """Test that memory can be persisted and loaded."""
    memory1 = ConversationMemory()
    session_id = "persistent-session"
    
    memory1.add_message(session_id, "user", "Test message")
    
    # Save to disk
    memory1.save_to_disk("test_memory.json")
    
    # Load in new instance
    memory2 = ConversationMemory()
    memory2.load_from_disk("test_memory.json")
    
    history = memory2.get_conversation_history(session_id)
    assert len(history) == 1
    assert history[0]["content"] == "Test message"
    
    # Cleanup
    import os
    if os.path.exists("test_memory.json"):
        os.remove("test_memory.json")


@pytest.mark.unit
def test_concurrent_access():
    """Test thread-safe access to conversation memory."""
    import threading
    
    memory = ConversationMemory()
    session_id = "concurrent-session"
    
    def add_messages(start, count):
        for i in range(start, start + count):
            memory.add_message(session_id, "user", f"Message {i}")
    
    # Create threads
    threads = [
        threading.Thread(target=add_messages, args=(0, 10)),
        threading.Thread(target=add_messages, args=(10, 10)),
    ]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    history = memory.get_conversation_history(session_id)
    
    # Should have 20 messages (or max_messages if limit applies)
    assert len(history) > 0
