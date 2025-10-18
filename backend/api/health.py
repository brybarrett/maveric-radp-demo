"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db
from loguru import logger
import os

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    Returns API status
    """
    return {
        "status": "healthy",
        "service": "docbot-platform",
        "client": os.getenv("CLIENT", "unknown"),
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }


@router.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """
    Database health check
    Verifies database connection is working
    """
    try:
        # Simple query to check connection
        await db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@router.get("/health/rag")
async def rag_health_check():
    """
    RAG engine health check
    Verifies RAG system is loaded and ready
    """
    from main import rag_engine
    
    if rag_engine is None:
        return {
            "status": "unhealthy",
            "rag_engine": "not initialized"
        }
    
    try:
        doc_count = rag_engine.get_document_count()
        return {
            "status": "healthy",
            "rag_engine": "initialized",
            "documents_loaded": doc_count,
            "client": rag_engine.client
        }
    except Exception as e:
        logger.error(f"RAG health check failed: {e}")
        return {
            "status": "unhealthy",
            "rag_engine": "error",
            "error": str(e)
        }