"""
Chat endpoints for DocBot Platform
Handles conversational interactions with the RAG-powered chatbot
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import uuid
from datetime import datetime

from models.database import get_db
from models.conversation import Conversation, Message
from rag.engine import RAGEngine
from chat.conversation_manager import ConversationManager

router = APIRouter()


# Dependency function to get RAG engine
def get_rag_dependency():
    """Get RAG engine from main module at runtime"""
    from main import rag_engine
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")
    return rag_engine


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request from user"""
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    mode: Optional[str] = Field("full_overview", description="Conversation mode: full_overview, module_deep_dive, or general")
    module: Optional[str] = Field(None, description="Specific module to explore (if mode=module_deep_dive)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "How do I train a Digital Twin?",
                "session_id": "abc123",
                "mode": "full_overview"
            }
        }


class ChatResponse(BaseModel):
    """Chat response to user"""
    response: str = Field(..., description="Bot's response message")
    session_id: str = Field(..., description="Session ID for this conversation")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Source documents used for response")
    visualization: Optional[Dict[str, Any]] = Field(None, description="Optional visualization data (Mermaid diagram)")
    suggestions: Optional[List[str]] = Field(None, description="Suggested follow-up questions")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "To train a Digital Twin, you'll need to provide UE training data and topology information...",
                "session_id": "abc123",
                "sources": [{"doc": "maveric_readme.md", "section": "Train API"}],
                "suggestions": ["Show me code example", "What is UE training data?"],
                "timestamp": "2025-01-15T10:30:00"
            }
        }


class SessionHistoryResponse(BaseModel):
    """Conversation history for a session"""
    session_id: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    rag_engine: RAGEngine = Depends(get_rag_dependency)
):
    """
    Main chat endpoint
    Handles user messages and returns AI-generated responses
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Chat request - Session: {session_id}, Mode: {request.mode}, Message: {request.message[:50]}...")
        
        # Initialize conversation manager
        conversation_manager = ConversationManager(
            db=db,
            rag_engine=rag_engine,
            session_id=session_id
        )
        
        # Get or create conversation session
        await conversation_manager.get_or_create_session()
        
        # Process the user's message
        response_data = await conversation_manager.process_message(
            user_message=request.message,
            mode=request.mode,
            module=request.module
        )
        
        # Save messages to database
        await conversation_manager.save_messages(
            user_message=request.message,
            bot_response=response_data["response"]
        )
        
        logger.info(f"Chat response generated - Session: {session_id}")
        
        return ChatResponse(
            response=response_data["response"],
            session_id=session_id,
            sources=response_data.get("sources"),
            visualization=response_data.get("visualization"),
            suggestions=response_data.get("suggestions")
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")


@router.get("/chat/history/{session_id}", response_model=SessionHistoryResponse)
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve conversation history for a session
    """
    try:
        conversation_manager = ConversationManager(
            db=db,
            rag_engine=None,  # Not needed for history retrieval
            session_id=session_id
        )
        
        history = await conversation_manager.get_conversation_history()
        
        if not history:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.delete("/chat/session/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation session and its history
    """
    try:
        conversation_manager = ConversationManager(
            db=db,
            rag_engine=None,
            session_id=session_id
        )
        
        deleted = await conversation_manager.delete_session()
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "status": "success",
            "message": f"Session {session_id} deleted",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@router.get("/chat/modes")
async def get_available_modes():
    """
    Get available conversation modes and modules
    """
    return {
        "modes": [
            {
                "id": "full_overview",
                "name": "Full Overview",
                "description": "Step-by-step guided tour of the entire workflow"
            },
            {
                "id": "module_deep_dive",
                "name": "Module Deep-Dive",
                "description": "In-depth exploration of a specific module",
                "requires_module": True
            },
            {
                "id": "general",
                "name": "General Q&A",
                "description": "Ask any question about the platform"
            }
        ],
        "modules": [
            "Digital Twin",
            "RF Prediction",
            "UE Tracks",
            "Orchestration"
        ]
    }