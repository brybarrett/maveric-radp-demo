"""
Database models for conversations and messages
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from models.database import Base


def generate_uuid():
    """Generate UUID as string"""
    return str(uuid.uuid4())


class Conversation(Base):
    """
    Conversation session model
    Tracks individual chat sessions
    """
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, unique=True, nullable=False, index=True)
    client = Column(String, nullable=False)  # maveric, demo, etc.
    mode = Column(String, default="full_overview")  # Conversation mode
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(session_id={self.session_id}, client={self.client})>"


class Message(Base):
    """
    Individual message model
    Stores user and bot messages
    """
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # Source documents used for this response
    visualization = Column(JSON, nullable=True)  # Visualization data if generated
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(role={self.role}, timestamp={self.timestamp})>"