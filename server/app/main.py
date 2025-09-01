"""
FastAPI application for the conversational AI agent.
Provides authentication endpoints and protected chat functionality.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging
import asyncio
import logging
import asyncio
from typing import Dict, Any, Optional

# Import application modules
from app.config import settings
from app.auth import (
    UserCreate, UserLogin, Token, get_current_user, 
    register_user, login_user
)
from app.db_utils import init_database, seed_mock_data
from app.pinecone_utils import init_pinecone
from app.agent import create_agent, create_simple_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request/Response Models
class ChatRequest(BaseModel):
    """Model for chat request."""
    query: str
    doc_ids: Optional[list[str]] = None
    verbose: Optional[bool] = False

class ChatResponse(BaseModel):
    """Model for chat response."""
    answer: str
    user_id: str
    query: str
    reasoning_steps: Optional[list] = None
    success: bool = True

class HealthResponse(BaseModel):
    """Model for health check response."""
    status: str
    message: str
    database_connected: bool
    pinecone_connected: bool

# Startup/Shutdown Event Handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    logger.info("Starting AI Agent API...")
    
    # Startup operations
    startup_success = True
    
    # Initialize MongoDB
    try:
        if init_database():
            logger.info("✅ MongoDB initialized successfully")
        else:
            logger.error("❌ MongoDB initialization failed")
            startup_success = False
    except Exception as e:
        logger.error(f"❌ Database startup error: {e}")
        startup_success = False
    
    # Initialize Pinecone
    try:
        if init_pinecone():
            logger.info("✅ Pinecone initialized successfully")
        else:
            logger.error("❌ Pinecone initialization failed")
            startup_success = False
    except Exception as e:
        logger.error(f"❌ Pinecone startup error: {e}")
        startup_success = False
    
    if startup_success:
        logger.info("🚀 AI Agent API startup completed successfully!")
    else:
        logger.warning("⚠️  AI Agent API started with some initialization issues")
    
    yield
    
    # Shutdown operations
    logger.info("Shutting down AI Agent API...")

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent API",
    description="Production-ready conversational AI agent with authentication and multi-source data access",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify system status.
    
    Returns:
        HealthResponse: System health information
    """
    try:
        # Test database connection
        from app.db_utils import get_database
        db = get_database()
        db_connected = db is not None
        
        # Test Pinecone connection  
        from app.pinecone_utils import get_index
        index = get_index()
        pinecone_connected = index is not None
        
        overall_status = "healthy" if db_connected and pinecone_connected else "degraded"
        
        return HealthResponse(
            status=overall_status,
            message="AI Agent API is running",
            database_connected=db_connected,
            pinecone_connected=pinecone_connected
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy", 
            message=f"Health check failed: {str(e)}",
            database_connected=False,
            pinecone_connected=False
        )

# Authentication Endpoints
@app.post("/register", response_model=Dict[str, Any])
async def register_endpoint(user_data: UserCreate):
    """
    Register a new user account.
    
    Args:
        user_data: User registration information
        
    Returns:
        Success message with user information
        
    Raises:
        HTTPException: If registration fails or user already exists
    """
    try:
        logger.info(f"Registration attempt for email: {user_data.email}")
        result = register_user(user_data)
        logger.info(f"Successfully registered user: {user_data.email}")
        return result
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Registration error for {user_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/login", response_model=Token)
async def login_endpoint(user_data: UserLogin):
    """
    Authenticate user and return JWT token.
    
    Args:
        user_data: User login credentials
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If login fails
    """
    try:
        logger.info(f"Login attempt for email: {user_data.email}")
        token = login_user(user_data)
        logger.info(f"Successfully authenticated user: {user_data.email}")
        return token
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Login error for {user_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

# Protected Chat Endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    current_user: dict = Depends(get_current_user)
):
    """
    Process chat query with the AI agent (protected endpoint).
    
    This endpoint requires JWT authentication and provides personalized
    responses based on the user's data and conversation history.
    
    Args:
        request: Chat request containing user query and optional parameters
        current_user: Current authenticated user (injected by dependency)
        
    Returns:
        AI agent response with reasoning steps (if verbose)
        
    Raises:
        HTTPException: If chat processing fails
    """
    user_id = str(current_user["_id"])
    query = request.query.strip()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    try:
        logger.info(f"Chat request from user {user_id}: {query[:100]}...")
        
        # Create agent for this user
        try:
            agent = create_agent(
                user_id=user_id, 
                doc_ids=request.doc_ids
            )
        except Exception as agent_error:
            logger.warning(f"Failed to create full agent, using simple fallback: {agent_error}")
            agent = create_simple_agent(user_id=user_id)
        
        # Process the query
        response = await asyncio.to_thread(
            agent.invoke, 
            {"input": query}
        )
        
        # Extract response components
        answer = response.get("output", "I apologize, but I couldn't generate a response.")
        intermediate_steps = response.get("intermediate_steps", []) if request.verbose else None
        
        # Format reasoning steps for verbose output
        reasoning_steps = None
        if request.verbose and intermediate_steps:
            reasoning_steps = []
            for step in intermediate_steps:
                if len(step) >= 2:
                    action = step[0]
                    observation = step[1]
                    reasoning_steps.append({
                        "tool": action.tool if hasattr(action, 'tool') else "unknown",
                        "input": action.tool_input if hasattr(action, 'tool_input') else {},
                        "output": observation[:500] + "..." if len(str(observation)) > 500 else str(observation)
                    })
        
        logger.info(f"Successfully processed chat request for user {user_id}")
        
        return ChatResponse(
            answer=answer,
            user_id=user_id,
            query=query,
            reasoning_steps=reasoning_steps,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Chat processing error for user {user_id}: {e}")
        
        # Return a graceful error response instead of raising HTTP exception
        return ChatResponse(
            answer=f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again or contact support if the issue persists.",
            user_id=user_id,
            query=query,
            reasoning_steps=None,
            success=False
        )

# User Profile Endpoint (Optional)
@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user's profile information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile information (excluding sensitive data)
    """
    try:
        from app.pinecone_utils import get_total_faq_count
        
        user_id = str(current_user["_id"])
        faq_count = get_total_faq_count()
        
        return {
            "user_id": user_id,
            "name": current_user.get("name"),
            "email": current_user.get("email"),
            "company_faq_count": faq_count,
            "created_at": current_user.get("created_at")
        }
        
    except Exception as e:
        logger.error(f"Error getting profile for user {current_user.get('email')}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Agent API",
        "version": "1.0.0",
        "description": "Production-ready conversational AI agent with authentication",
        "endpoints": {
            "health": "GET /health - System health check",
            "register": "POST /register - User registration",
            "login": "POST /login - User authentication", 
            "chat": "POST /chat - Chat with AI agent (protected)",
            "profile": "GET /profile - User profile (protected)"
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return {"error": "Endpoint not found", "detail": f"The requested endpoint was not found."}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {exc}")
    return {"error": "Internal server error", "detail": "An unexpected error occurred."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
