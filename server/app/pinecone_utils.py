"""
Pinecone vector database utilities for document storage and semantic search.
Handles document embedding, storage, and retrieval for FAQ and notes.
"""

# Pinecone and embedding model setup utilities
from app.config import settings
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import logging
import uuid
import time
from typing import List, Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pinecone client
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# Get Pinecone index and embedding model
index = pc.Index(settings.PINECONE_INDEX_NAME)
embeddings = GoogleGenerativeAIEmbeddings(model=settings.GEMINI_EMBEDDING_MODEL, google_api_key=settings.GEMINI_API_KEY)

def init_pinecone():
    """
    Initialize Pinecone client and connect to index.
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        logger.info(f"Connecting to Pinecone index: {settings.PINECONE_INDEX_NAME}")
        
        # Test connection by getting index stats
        stats = index.describe_index_stats()
        logger.info(f"Successfully connected to Pinecone index. Total vectors: {stats.total_vector_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone: {e}")
        return False

def get_index():
    """Get Pinecone index instance."""
    return index

def get_embeddings():
    """Get embeddings instance."""
    return embeddings

def upsert_faq_document(
    text: str, 
    doc_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Embed and store a company FAQ document in Pinecone (accessible to all users).
    
    Args:
        text: FAQ document text to embed and store
        doc_id: Optional document ID (will generate if not provided)
        metadata: Optional additional metadata
        
    Returns:
        str: Document ID of the stored document
        
    Raises:
        Exception: If document storage fails
    """
    try:
        # Generate doc_id if not provided
        if not doc_id:
            doc_id = str(uuid.uuid4())
        
        # Create embedding vector
        vector = embeddings.embed_query(text)
        
        # Prepare metadata (no user_id - accessible to all)
        doc_metadata = {
            "doc_id": doc_id,
            "text": text,
            "created_at": time.time(),
            "document_type": "company_faq"
        }
        
        # Add additional metadata if provided
        if metadata:
            doc_metadata.update(metadata)
        
        # Upsert to Pinecone
        index.upsert(
            vectors=[(doc_id, vector, doc_metadata)]
        )
        
        logger.info(f"Successfully stored company FAQ document {doc_id}")
        return doc_id
        
    except Exception as e:
        logger.error(f"Error storing FAQ document: {e}")
        raise

def search_faq_documents(
    query: str, 
    top_k: int = 5,
    min_similarity: float = 0.7
) -> Dict[str, Any]:
    """
    Search company FAQ documents using semantic similarity (accessible to all users).
    
    Args:
        query: Search query text
        top_k: Number of top results to return
        min_similarity: Minimum similarity score threshold
        
    Returns:
        Dictionary containing search results and metadata
    """
    try:
        # Create query embedding
        query_vector = embeddings.embed_query(query)
        
        # Query Pinecone (no user filtering - search all company FAQs)
        response = index.query(
            vector=query_vector,
            filter={"document_type": "company_faq"},  # Only search company FAQs
            top_k=top_k,
            include_metadata=True,
            include_values=False
        )
        
        # Process results
        matches = response.matches or []
        relevant_docs = []
        
        for match in matches:
            similarity_score = match.score
            
            # Apply similarity threshold
            if similarity_score >= min_similarity:
                relevant_docs.append({
                    "doc_id": match.metadata.get("doc_id"),
                    "text": match.metadata.get("text", ""),
                    "similarity": similarity_score,
                    "metadata": match.metadata
                })
        
        # Combine all relevant text
        combined_text = "\n\n".join([doc["text"] for doc in relevant_docs])
        
        result = {
            "query": query,
            "found_documents": len(relevant_docs),
            "total_matches": len(matches),
            "combined_text": combined_text,
            "documents": relevant_docs,
            "search_successful": True
        }
        
        # Add context about search quality
        if not relevant_docs:
            result["message"] = f"No FAQ documents found with similarity >= {min_similarity}"
            result["search_successful"] = False
        elif len(relevant_docs) < len(matches):
            result["message"] = f"Found {len(relevant_docs)} highly relevant FAQ documents out of {len(matches)} total matches"
        
        logger.info(f"Search completed: {len(relevant_docs)} relevant FAQ docs found")
        return result
        
    except Exception as e:
        logger.error(f"Error searching FAQ documents: {e}")
        return {
            "query": query,
            "found_documents": 0,
            "total_matches": 0,
            "combined_text": "",
            "documents": [],
            "search_successful": False,
            "error": str(e)
        }

    """
    Delete a company FAQ document from Pinecone.
    
    Args:
        doc_id: Document ID to delete
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        # Verify document exists and is a company FAQ
        query_response = index.query(
            id=doc_id,
            top_k=1,
            include_metadata=True,
            filter={"document_type": "company_faq"}
        )
        
        if not query_response.matches:
            logger.warning(f"Company FAQ document {doc_id} not found")
            return False
        
        # Delete the document
        index.delete(ids=[doc_id])
        logger.info(f"Successfully deleted company FAQ document {doc_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting FAQ document {doc_id}: {e}")
        return False

    """
    Get the total count of company FAQ documents.
    
    Returns:
        int: Number of company FAQ documents
    """
    try:
        # Query with a dummy vector to get count
        dummy_vector = [0.0] * 768  # Gemini embedding dimension
        
        response = index.query(
            vector=dummy_vector,
            filter={"document_type": "company_faq"},
            top_k=10000,  # Large number to get all docs
            include_metadata=False
        )
        
        return len(response.matches or [])
        
    except Exception as e:
        logger.error(f"Error getting FAQ document count: {e}")
        return 0