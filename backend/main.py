"""
DocBot Platform - Main FastAPI Application
AI-powered interactive documentation chatbot
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from loguru import logger

from api.chat import router as chat_router
from api.health import router as health_router
from rag.engine import RAGEngine
from models.database import init_db

# Load environment variables
load_dotenv()

# DEBUG: Print the actual DATABASE_URL being used
logger.critical("="*80)
logger.critical(f"DATABASE_URL from environment: {os.getenv('DATABASE_URL', 'NOT SET')}")
logger.critical("="*80)

# Configuration
CLIENT = os.getenv("CLIENT", "maveric")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Global RAG engine instance
rag_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Initializes resources on startup, cleans up on shutdown
    """
    global rag_engine
    
    logger.info(f"Starting DocBot Platform - Client: {CLIENT}, Environment: {ENVIRONMENT}")
    
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    
    # Initialize RAG engine with client-specific configuration
    logger.info(f"Loading RAG engine for client: {CLIENT}")
    docs_path = f"examples/{CLIENT}/docs/"
    
    try:
        rag_engine = RAGEngine(client=CLIENT, docs_path=docs_path)
        await rag_engine.initialize()
        logger.info("RAG engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG engine: {e}")
        raise
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down DocBot Platform...")
    if rag_engine:
        await rag_engine.cleanup()


# Create FastAPI app
app = FastAPI(
    title="DocBot Platform API",
    description="AI-powered interactive documentation chatbot",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "DocBot Platform API",
        "version": "1.0.0",
        "client": CLIENT,
        "environment": ENVIRONMENT,
        "docs": "/docs" if DEBUG else "disabled in production"
    }


# Dependency to get RAG engine
def get_rag_engine() -> RAGEngine:
    """Dependency injection for RAG engine"""
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")
    return rag_engine


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=DEBUG,
        log_level="info" if DEBUG else "warning"
    )