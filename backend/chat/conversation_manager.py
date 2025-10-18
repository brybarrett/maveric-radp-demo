"""
Conversation Manager
Handles conversation flow, context management, and orchestrates RAG + LLM
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from datetime import datetime

from models.conversation import Conversation, Message
from rag.engine import RAGEngine


class ConversationManager:
    """
    Manages conversation sessions and orchestrates RAG/LLM interactions
    """
    
    def __init__(self, db: AsyncSession, rag_engine: Optional[RAGEngine], session_id: str):
        """
        Initialize conversation manager
        
        Args:
            db: Database session
            rag_engine: RAG engine instance
            session_id: Unique session identifier
        """
        self.db = db
        self.rag_engine = rag_engine
        self.session_id = session_id
        self.conversation = None
        
        logger.info(f"ConversationManager initialized for session: {session_id}")
    
    async def get_or_create_session(self) -> Conversation:
        """
        Get existing conversation or create new one
        
        Returns:
            Conversation object
        """
        # Check if conversation exists
        result = await self.db.execute(
            select(Conversation).where(Conversation.session_id == self.session_id)
        )
        conversation = result.scalar_one_or_none()
        
        if conversation:
            logger.info(f"Found existing conversation: {self.session_id}")
            self.conversation = conversation
        else:
            # Create new conversation
            logger.info(f"Creating new conversation: {self.session_id}")
            conversation = Conversation(
                session_id=self.session_id,
                client=self.rag_engine.client if self.rag_engine else "unknown"
            )
            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)
            self.conversation = conversation
        
        return self.conversation
    
    async def process_message(
        self,
        user_message: str,
        mode: str = "full_overview",
        module: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response
        
        Args:
            user_message: User's input message
            mode: Conversation mode (full_overview, module_deep_dive, general)
            module: Specific module if in deep-dive mode
            
        Returns:
            Dict containing response, sources, visualizations, suggestions
        """
        logger.info(f"Processing message in mode '{mode}': {user_message[:50]}...")
        
        # Get conversation history
        history = await self._get_message_history()
        
        # Retrieve relevant context from RAG
        context = await self.rag_engine.retrieve(user_message)
        
        # Generate response
        response_data = await self.rag_engine.generate_response(
            query=user_message,
            context=context,
            conversation_history=history,
            mode=mode
        )
        
        # Add suggestions for follow-up questions
        suggestions = self._generate_suggestions(mode, module)
        response_data["suggestions"] = suggestions
        
        # Generate visualization if applicable
        visualization = await self._generate_visualization(user_message, mode)
        if visualization:
            response_data["visualization"] = visualization
        
        logger.info(f"Response generated for session: {self.session_id}")
        return response_data
    
    async def _get_message_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get conversation message history
        
        Args:
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dicts with role and content
        """
        if not self.conversation:
            return []
        
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == self.conversation.id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
        )
        
        messages = result.scalars().all()
        
        # Reverse to get chronological order
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]
    
    def _generate_suggestions(self, mode: str, module: Optional[str]) -> List[str]:
        """
        Generate contextual follow-up question suggestions
        
        Args:
            mode: Current conversation mode
            module: Current module (if in deep-dive)
            
        Returns:
            List of suggested questions
        """
        suggestions = []
        
        if mode == "full_overview":
            suggestions = [
                "Show me a code example",
                "Explain this step in more detail",
                "What are common mistakes to avoid?",
                "Can you visualize this workflow?"
            ]
        elif mode == "module_deep_dive":
            if module == "Digital Twin":
                suggestions = [
                    "How do I tune the training parameters?",
                    "What data format is required?",
                    "Show me a training example",
                    "What happens if training fails?"
                ]
            elif module == "RF Prediction":
                suggestions = [
                    "How accurate are the predictions?",
                    "Can I adjust antenna parameters?",
                    "Show me prediction output format",
                    "How long does prediction take?"
                ]
            elif module == "UE Tracks":
                suggestions = [
                    "How do I generate custom UE paths?",
                    "What's the difference between UE classes?",
                    "Show me UE data format",
                    "Can I upload my own UE data?"
                ]
            elif module == "Orchestration":
                suggestions = [
                    "How are jobs scheduled?",
                    "What happens if a job fails?",
                    "Can I run jobs in parallel?",
                    "How do I monitor job status?"
                ]
            else:
                suggestions = [
                    "Tell me more about this",
                    "Show me an example",
                    "What are the next steps?"
                ]
        else:
            suggestions = [
                "Can you explain that differently?",
                "Show me a related topic",
                "What should I learn next?"
            ]
        
        return suggestions[:4]  # Return top 4 suggestions
    
    async def _generate_visualization(
        self,
        user_message: str,
        mode: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate visualization if the query warrants it
        
        Args:
            user_message: User's message
            mode: Conversation mode
            
        Returns:
            Visualization data (Mermaid diagram) or None
        """
        # Keywords that suggest visualization would be helpful
        viz_keywords = [
            "workflow", "flow", "steps", "process", "how does",
            "explain", "visualize", "show me", "diagram"
        ]
        
        # Check if user is asking for a visualization
        should_visualize = any(keyword in user_message.lower() for keyword in viz_keywords)
        
        if not should_visualize:
            return None
        
        # Generate appropriate Mermaid diagram based on mode
        if mode == "full_overview":
            # Overall workflow visualization
            diagram = self._create_workflow_diagram()
        else:
            # Simplified diagram
            diagram = self._create_simple_diagram()
        
        return {
            "type": "mermaid",
            "content": diagram,
            "title": "Workflow Visualization"
        }
    
    def _create_workflow_diagram(self) -> str:
        """
        Create Mermaid diagram for full workflow
        
        Returns:
            Mermaid diagram string
        """
        return """graph LR
    A[Start] --> B[Prepare Training Data]
    B --> C[Train Digital Twin]
    C --> D[Generate UE Tracks]
    D --> E[Run RF Prediction]
    E --> F[Orchestrate Jobs]
    F --> G[Collect Results]
    G --> H[Analyze Output]
    H --> I[End]
    
    style C fill:#4A90E2
    style E fill:#4A90E2
    style F fill:#4A90E2"""
    
    def _create_simple_diagram(self) -> str:
        """
        Create simplified Mermaid diagram
        
        Returns:
            Mermaid diagram string
        """
        return """graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    
    style B fill:#4A90E2"""
    
    async def save_messages(self, user_message: str, bot_response: str):
        """
        Save user and bot messages to database
        
        Args:
            user_message: User's message
            bot_response: Bot's response
        """
        if not self.conversation:
            logger.warning("No conversation found, cannot save messages")
            return
        
        # Save user message
        user_msg = Message(
            conversation_id=self.conversation.id,
            role="user",
            content=user_message
        )
        self.db.add(user_msg)
        
        # Save bot message
        bot_msg = Message(
            conversation_id=self.conversation.id,
            role="assistant",
            content=bot_response
        )
        self.db.add(bot_msg)
        
        # Update conversation timestamp
        self.conversation.updated_at = datetime.utcnow()
        
        await self.db.commit()
        logger.info(f"Messages saved for session: {self.session_id}")
    
    async def get_conversation_history(self) -> Optional[Dict[str, Any]]:
        """
        Get full conversation history
        
        Returns:
            Dict with conversation metadata and messages
        """
        if not self.conversation:
            # Try to load conversation
            result = await self.db.execute(
                select(Conversation).where(Conversation.session_id == self.session_id)
            )
            self.conversation = result.scalar_one_or_none()
        
        if not self.conversation:
            return None
        
        # Get all messages
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == self.conversation.id)
            .order_by(Message.timestamp.asc())
        )
        messages = result.scalars().all()
        
        return {
            "session_id": self.conversation.session_id,
            "created_at": self.conversation.created_at,
            "updated_at": self.conversation.updated_at,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "sources": msg.sources,
                    "visualization": msg.visualization
                }
                for msg in messages
            ]
        }
    
    async def delete_session(self) -> bool:
        """
        Delete conversation session
        
        Returns:
            True if deleted, False if not found
        """
        if not self.conversation:
            result = await self.db.execute(
                select(Conversation).where(Conversation.session_id == self.session_id)
            )
            self.conversation = result.scalar_one_or_none()
        
        if not self.conversation:
            return False
        
        await self.db.delete(self.conversation)
        await self.db.commit()
        
        logger.info(f"Deleted conversation session: {self.session_id}")
        return True