"""
Authentication utilities for JWT token management and user verification.
Handles user registration, login, password hashing, and token validation.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from app.config import settings
from app.db_utils import get_user_by_email, create_user, get_user

# HTTP Bearer security scheme
security = HTTPBearer()

class UserCreate(BaseModel):
    """Model for user registration."""
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    """Model for user login."""
    email: str
    password: str

class Token(BaseModel):
    """Model for JWT token response."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Model for JWT token data."""
    user_id: Optional[str] = None

def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verify a plain password against stored password (for testing - no hashing).
    
    Args:
        plain_password: The plain text password
        stored_password: The stored password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    return plain_password == stored_password

def get_password_hash(password: str) -> str:
    """
    Store password in plain text (for testing purposes only).
    
    Args:
        password: Plain text password
        
    Returns:
        Plain text password (no hashing for testing)
    """
    return password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing token payload data
        expires_delta: Token expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def authenticate_user(email: str, password: str) -> Optional[dict]:
    """
    Authenticate a user with email and password.
    
    Args:
        email: User's email address
        password: Plain text password
        
    Returns:
        User document if authentication successful, None otherwise
    """
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials containing the JWT token
        
    Returns:
        User document from database
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # Get user from database
    user = get_user(user_id)
    if user is None:
        raise credentials_exception
        
    return user

def register_user(user_data: UserCreate) -> dict:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        
    Returns:
        Dictionary containing success message and user info
        
    Raises:
        HTTPException: If user already exists
    """
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Store password in plain text (for testing) and create user
    password_plain = get_password_hash(user_data.password)
    user = create_user(user_data.name, user_data.email, password_plain)
    
    return {
        "message": "User created successfully",
        "user_id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"]
    }

def login_user(user_data: UserLogin) -> Token:
    """
    Log in a user and return JWT token.
    
    Args:
        user_data: User login credentials
        
    Returns:
        JWT token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token)
