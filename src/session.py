"""Session management for chat history."""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class Session:
    """Chat session with history."""
    
    def __init__(self, session_id: Optional[str] = None, ttl_hours: int = 24):
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(hours=ttl_hours)
        self.history: List[Dict[str, str]] = []
    
    def add_message(self, question: str, answer: str) -> None:
        self.history.append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
    
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

class SessionManager:
    """Manages multiple chat sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            if not session.is_expired():
                return session
        
        session = Session(session_id)
        self.sessions[session.session_id] = session
        return session