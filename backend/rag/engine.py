"""
RAG (Retrieval Augmented Generation) Engine
Handles document loading, embedding, retrieval, and context generation
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import anthropic
from dotenv import load_dotenv

load_dotenv()


class RAGEngine:
    """
    RAG Engine for document retrieval and context generation
    """
    
    def __init__(self, client: str, docs_path: str):
        """
        Initialize RAG engine
        
        Args:
            client: Client name (maveric, demo, etc.)
            docs_path: Path to documentation files
        """
        self.client = client
        self.docs_path = Path(docs_path)
        self.config = self._load_config()
        
        # Embedding model
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.embedding_model = None
        
        # Vector database
        self.chroma_client = None
        self.collection = None
        
        # LLM client
        self.llm_provider = os.getenv("LLM_PROVIDER", "anthropic")
        self.llm_model = os.getenv("LLM_MODEL", "claude-sonnet-4-5-20250929")
        self.anthropic_client = None
        
        # Configuration
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 500))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 50))
        self.max_results = int(os.getenv("MAX_RESULTS", 5))
        
        logger.info(f"RAG Engine initialized for client: {client}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load client-specific configuration"""
        config_path = Path(f"examples/{self.client}/config/config.json")
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {
                "client_name": self.client,
                "modules": [],
                "enable_visualizations": True
            }
        
        with open(config_path, 'r') as f:
            config = json.load(f)
            logger.info(f"Loaded config for {self.client}")
            return config
    
    async def initialize(self):
        """
        Initialize all components asynchronously
        """
        logger.info("Initializing RAG engine components...")
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Initialize ChromaDB
        logger.info("Initializing ChromaDB...")
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Create or get collection
        collection_name = f"docbot_{self.client}"
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"client": self.client}
        )
        
        # Initialize LLM client
        if self.llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        
        # Load and embed documents
        await self._load_documents()
        
        logger.info("RAG engine initialization complete")
    
    async def _load_documents(self):
        """
        Load documentation files and create embeddings
        """
        if not self.docs_path.exists():
            logger.warning(f"Documentation path does not exist: {self.docs_path}")
            return
        
        # Get all markdown files
        doc_files = list(self.docs_path.glob("*.md"))
        
        if not doc_files:
            logger.warning(f"No documentation files found in {self.docs_path}")
            return
        
        logger.info(f"Found {len(doc_files)} documentation files")
        
        all_chunks = []
        all_embeddings = []
        all_metadatas = []
        all_ids = []
        
        for doc_file in doc_files:
            logger.info(f"Processing {doc_file.name}...")
            
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chunk the document
            chunks = self._chunk_document(content)
            
            # Create embeddings
            for idx, chunk in enumerate(chunks):
                chunk_id = f"{doc_file.stem}_{idx}"
                embedding = self.embedding_model.encode(chunk).tolist()
                
                all_chunks.append(chunk)
                all_embeddings.append(embedding)
                all_metadatas.append({
                    "source": doc_file.name,
                    "chunk_id": chunk_id,
                    "client": self.client
                })
                all_ids.append(chunk_id)
        
        # Add to ChromaDB
        if all_chunks:
            self.collection.add(
                documents=all_chunks,
                embeddings=all_embeddings,
                metadatas=all_metadatas,
                ids=all_ids
            )
            logger.info(f"Added {len(all_chunks)} chunks to vector database")
    
    def _chunk_document(self, content: str) -> List[str]:
        """
        Split document into overlapping chunks
        
        Args:
            content: Document content
            
        Returns:
            List of text chunks
        """
        # Simple character-based chunking
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + self.chunk_size
            chunk = content[start:end]
            
            # Try to break at sentence boundary
            if end < len(content):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > 0:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - self.chunk_overlap
        
        return [c for c in chunks if c]  # Remove empty chunks
    
    async def retrieve(self, query: str, n_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a query
        
        Args:
            query: User's query
            n_results: Number of results to return (default: self.max_results)
            
        Returns:
            List of relevant document chunks with metadata
        """
        if n_results is None:
            n_results = self.max_results
        
        # Create query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        retrieved_docs = []
        if results and results['documents']:
            for idx, doc in enumerate(results['documents'][0]):
                retrieved_docs.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][idx],
                    "distance": results['distances'][0][idx] if 'distances' in results else None
                })
        
        logger.info(f"Retrieved {len(retrieved_docs)} relevant chunks for query: {query[:50]}...")
        return retrieved_docs
    
    async def generate_response(
        self,
        query: str,
        context: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        mode: str = "full_overview"
    ) -> Dict[str, Any]:
        """
        Generate response using LLM with retrieved context
        
        Args:
            query: User's query
            context: Retrieved document chunks
            conversation_history: Previous conversation messages
            mode: Conversation mode
            
        Returns:
            Dict with response and metadata
        """
        # Build context string
        context_str = "\n\n".join([f"Source: {doc['metadata']['source']}\n{doc['content']}" for doc in context])
        
        # Build system prompt
        system_prompt = self._build_system_prompt(mode)
        
        # Build conversation messages
        messages = []
        
        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current query with context
        user_message = f"""Context from documentation:
{context_str}

User question: {query}

Please provide a clear, technical response based on the documentation above."""

        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Generate response with Claude
        if self.llm_provider == "anthropic":
            response = self.anthropic_client.messages.create(
                model=self.llm_model,
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", 2000)),
                temperature=float(os.getenv("LLM_TEMPERATURE", 0.7)),
                system=system_prompt,
                messages=messages
            )
            
            response_text = response.content[0].text
        else:
            # Fallback if other providers added later
            response_text = "LLM provider not configured"
        
        # Extract sources
        sources = [{"source": doc["metadata"]["source"]} for doc in context]
        
        return {
            "response": response_text,
            "sources": sources,
            "mode": mode
        }
    
    def _build_system_prompt(self, mode: str) -> str:
        """
        Build system prompt based on conversation mode
        
        Args:
            mode: Conversation mode
            
        Returns:
            System prompt string
        """
        # Extract module names from config (handles both dict and string formats)
        modules = self.config.get('modules', [])
        if modules and isinstance(modules[0], dict):
            module_names = [m.get('name', '') for m in modules]
        else:
            module_names = modules
        
        modules_str = ', '.join(module_names) if module_names else 'various topics'
        
        base_prompt = f"""You are a technical documentation assistant for {self.config.get('client_name', self.client)}.

Your role is to provide accurate, clear explanations of technical workflows and system capabilities.

Available modules: {modules_str}

Response guidelines:
- Provide clear, technically accurate information
- Use proper formatting: code blocks for code, numbered lists for procedures, bullet points for features
- Include relevant code examples from the documentation when applicable
- Structure responses with headers for complex topics
- Cite specific documentation sources
- Maintain a professional, technical tone
- Do not use emojis or overly casual language
- Focus on precision and clarity over friendliness

When providing code examples:
- Use proper syntax highlighting with language specification
- Include brief explanations of what the code does
- Show realistic parameter values from the documentation

When explaining workflows:
- Number the steps clearly
- Specify required inputs and expected outputs  
- Note any prerequisites or dependencies
- Reference related modules when relevant"""

        if mode == "full_overview":
            return base_prompt + "\n\nCurrent mode: Provide comprehensive, step-by-step workflow guidance covering the complete process from start to finish."
        elif mode == "module_deep_dive":
            return base_prompt + "\n\nCurrent mode: Provide detailed technical explanation of the specific module, including architecture, parameters, and usage patterns."
        else:
            return base_prompt + "\n\nCurrent mode: Provide direct, concise answers to specific technical questions."
    
    def get_document_count(self) -> int:
        """Get number of documents loaded"""
        if self.collection:
            return self.collection.count()
        return 0
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up RAG engine resources...")
        # Add any cleanup logic here