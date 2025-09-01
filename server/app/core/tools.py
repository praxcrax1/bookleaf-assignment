"""
LangChain tools for the conversational AI agent.
Provides tools for document search, book status lookup, and award status lookup.
"""
from typing import Annotated, Optional
from langchain.tools import tool
from langchain_core.tools import InjectedToolArg
from app.pinecone_utils import get_embeddings, get_index
from app.db_utils import get_book_status_by_user_id, get_award_status_by_user_id
import logging

logger = logging.getLogger(__name__)

@tool
def search_faq_documents(
    query: str
) -> str:
    """
    Search company FAQ documents using semantic similarity.
    
    This tool searches through company FAQ documents stored in Pinecone vector database
    to find information relevant to the user's query. These FAQs are accessible to all users
    and contain general information about the company's services and processes.
    
    Args:
        query: The search query text
        
    Returns:
        Combined text from relevant FAQ documents, or a message if no relevant documents found
    """
    try:
        logger.info(f"Searching company FAQ documents with query: {query[:100]}...")
        
        # Import the function locally to avoid circular imports
        from app.pinecone_utils import search_faq_documents as pinecone_search_faq
        
        # Perform semantic search on company FAQs
        search_results = pinecone_search_faq(
            query=query,
            top_k=15,
            min_similarity=0.7
        )
        
        if search_results["search_successful"] and search_results["found_documents"] > 0:
            # Add context about the search results
            context_info = f"Found {search_results['found_documents']} relevant FAQ documents:\n\n"
            return context_info + search_results["combined_text"]
        else:
            # No relevant documents found
            return f"I don't have sufficient information about this topic in our FAQ knowledge base. {search_results.get('message', '')}"
            
    except Exception as e:
        logger.error(f"Error in search_faq_documents tool: {e}")
        return f"I encountered an error while searching for FAQ information: {str(e)}"

@tool
def book_status_lookup(
    user_id: Annotated[str, InjectedToolArg],
    author_id: Optional[str] = None
) -> str:
    """
    Look up book status and progress for a user or specific author.
    
    This tool queries the MongoDB database to retrieve current book status,
    including stage information and editorial notes.
    
    Args:
        user_id: ID of the user making the request (automatically injected)  
        author_id: Optional specific author ID to look up (defaults to user_id)
        
    Returns:
        Formatted book status information or a message if no book found
    """
    try:
        # Use user_id as author_id if not specified
        target_author_id = author_id or user_id
        
        logger.info(f"Looking up book status for author {target_author_id}")
        
        book_info = get_book_status_by_user_id(target_author_id)
        
        if book_info:
            status_info = f"""Book Status Information:
Title: {book_info.get('title', 'N/A')}
Current Status: {book_info.get('status', 'Unknown')}
Stage Notes: {book_info.get('stage_notes', 'No notes available')}
Book ID: {book_info.get('book_id', 'N/A')}
"""
            return status_info
        else:
            return f"No book information found for the requested author. You may not have any books in our system yet."
            
    except Exception as e:
        logger.error(f"Error in book_status_lookup tool: {e}")
        return f"I encountered an error while looking up book status: {str(e)}"

@tool
def get_user_profile_summary(
    user_id: Annotated[str, InjectedToolArg]
) -> str:
    """
    Get a comprehensive summary of user's profile including books and awards.
    
    Args:
        user_id: ID of the user (automatically injected)
        
    Returns:
        Formatted summary of user's profile information
    """
    try:
        logger.info(f"Getting profile summary for user {user_id}")
        
        # Get book and award information
        book_info = get_book_status_by_user_id(user_id)
        
        summary_parts = ["Your Profile Summary:\n"]
        
        # Book information
        if book_info:
            summary_parts.append(f"📚 Book: '{book_info.get('title', 'N/A')}' - Status: {book_info.get('status', 'Unknown')}")
        else:
            summary_parts.append("📚 No books found in your profile")
            
        return "\n".join(summary_parts)
        
    except Exception as e:
        logger.error(f"Error in get_user_profile_summary tool: {e}")
        return f"I encountered an error while retrieving your profile summary: {str(e)}"
