from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json
import uuid

@dataclass
class ChatMessage:
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    message_id: str
    session_id: str

class ConversationManager:
    def __init__(self):
        self.sessions = {}  # session_id -> List[ChatMessage]
        self.current_session = None
    
    def start_new_session(self, initial_code: str) -> str:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        self.sessions[session_id] = [
            ChatMessage(
                role="system",
                content="You are ClippyAI, helping with code analysis and debugging.",
                timestamp=datetime.now(),
                message_id="sys_001",
                session_id=session_id
            ),
            ChatMessage(
                role="user", 
                content=f"Analyze this code/problem: {initial_code}",
                timestamp=datetime.now(),
                message_id="usr_001",
                session_id=session_id
            )
        ]
        self.current_session = session_id
        return session_id
    
    def add_message(self, role: str, content: str) -> None:
        if not self.current_session:
            return
            
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            message_id=f"{role}_{len(self.sessions[self.current_session])}",
            session_id=self.current_session
        )
        self.sessions[self.current_session].append(message)
    
    def get_conversation_context(self, max_messages: int = 10) -> List[dict]:
        if not self.current_session:
            return []
        
        messages = self.sessions[self.current_session][-max_messages:]
        return [
            {"role": msg.role, "content": msg.content} 
            for msg in messages
        ]
    
    def clear_current_session(self):
        self.current_session = None
