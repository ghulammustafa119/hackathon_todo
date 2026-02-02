"""Conversation state management for storing conversation history."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
from sqlmodel import Session
from src.database.session import get_session
from src.models.conversation import ConversationHistory, ConversationMessage


class ConversationStateManager:
    """Manages conversation history and state in the database."""

    def __init__(self):
        pass

    def store_conversation_message(self, user_id: str, role: str, content: str, conversation_id: Optional[str] = None):
        """Store a conversation message in the database."""
        # This is now handled by the API layer using conversation_service
        pass

    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations for a user."""
        # This is now handled by the conversation_service
        return []


# Global instance
conversation_manager = ConversationStateManager()