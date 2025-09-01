"""
Database utilities for MongoDB operations.
Handles user management, book status, award status, and mock data seeding.
"""
from typing import Optional, Dict, Any
from pymongo import MongoClient
from bson import ObjectId
from app.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MongoDB client
client = None
db = None

def init_database():
    """Initialize MongoDB connection and database."""
    global client, db
    try:
        client = MongoClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB]
        
        # Test connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes for better performance
        db.users.create_index("email", unique=True)
        db.books.create_index("author_id")
        db.awards.create_index("author_id")
        
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return False

def get_database():
    """Get database instance."""
    global db
    if db is None:
        init_database()
    return db

# User Management Functions

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by their email address.
    
    Args:
        email: User's email address
        
    Returns:
        User document if found, None otherwise
    """
    try:
        db = get_database()
        user = db.users.find_one({"email": email})
        return user
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {e}")
        return None

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by their ID.
    
    Args:
        user_id: User's ObjectId as string
        
    Returns:
        User document if found, None otherwise
    """
    try:
        db = get_database()
        user = db.users.find_one({"_id": ObjectId(user_id)})
        return user
    except Exception as e:
        logger.error(f"Error getting user by ID {user_id}: {e}")
        return None

def create_user(name: str, email: str, password: str) -> Dict[str, Any]:
    """
    Create a new user in the database.
    
    Args:
        name: User's full name
        email: User's email address
        password: Plain text password (for testing)
        
    Returns:
        Created user document
        
    Raises:
        Exception: If user creation fails
    """
    try:
        db = get_database()
        user_doc = {
            "name": name,
            "email": email,
            "password": password,
            "created_at": ObjectId().generation_time
        }
        
        result = db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        logger.info(f"Created user: {email}")
        return user_doc
        
    except Exception as e:
        logger.error(f"Error creating user {email}: {e}")
        raise

# Book Management Functions

def get_book_status(author_id: str) -> Optional[Dict[str, Any]]:
    """
    Get book status for a specific author.
    
    Args:
        author_id: Author's ID
        
    Returns:
        Book status document if found, None otherwise
    """
    try:
        db = get_database()
        book = db.books.find_one({"author_id": author_id})
        return book
    except Exception as e:
        logger.error(f"Error getting book status for author {author_id}: {e}")
        return None

def get_book_status_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get book status for a user (assuming user_id == author_id for simplicity).
    
    Args:
        user_id: User's ObjectId as string
        
    Returns:
        Book status document if found, None otherwise
    """
    return get_book_status(user_id)

# Award Management Functions

def get_award_status(author_id: str) -> Optional[Dict[str, Any]]:
    """
    Get award status for a specific author.
    
    Args:
        author_id: Author's ID
        
    Returns:
        Award status document if found, None otherwise
    """
    try:
        db = get_database()
        award = db.awards.find_one({"author_id": author_id})
        return award
    except Exception as e:
        logger.error(f"Error getting award status for author {author_id}: {e}")
        return None

def get_award_status_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get award status for a user (assuming user_id == author_id for simplicity).
    
    Args:
        user_id: User's ObjectId as string
        
    Returns:
        Award status document if found, None otherwise
    """
    return get_award_status(user_id)

# Chat History Management

def save_chat_message(user_id: str, message: str, response: str):
    """
    Save a chat interaction to the database.
    
    Args:
        user_id: User's ObjectId as string
        message: User's message
        response: Agent's response
    """
    try:
        db = get_database()
        chat_doc = {
            "user_id": user_id,
            "message": message,
            "response": response,
            "timestamp": ObjectId().generation_time
        }
        
        db.chat_histories.insert_one(chat_doc)
        logger.info(f"Saved chat message for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error saving chat message for user {user_id}: {e}")

# Mock Data Functions

def seed_mock_data():
    """
    Seed the database with mock data for testing.
    This function is safe to run multiple times.
    """
    try:
        db = get_database()
        
        # Clear existing mock data (optional - remove in production)
        logger.info("Seeding mock data...")
        
        # Mock Users (only if they don't exist)
        mock_users = [
            {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "password": "password123"  # Plain text for testing
            },
            {
                "name": "Bob Smith", 
                "email": "bob@example.com",
                "password": "password123"  # Plain text for testing
            }
        ]
        
        user_ids = []
        for user_data in mock_users:
            existing_user = db.users.find_one({"email": user_data["email"]})
            if not existing_user:
                user_data["created_at"] = ObjectId().generation_time
                result = db.users.insert_one(user_data)
                user_ids.append(str(result.inserted_id))
                logger.info(f"Created mock user: {user_data['email']}")
            else:
                user_ids.append(str(existing_user["_id"]))
                logger.info(f"Mock user already exists: {user_data['email']}")
        
        # Mock Books
        mock_books = [
            {
                "author_id": user_ids[0],
                "book_id": "book_001",
                "title": "The Digital Revolution",
                "status": "in_editing",
                "stage_notes": "Currently in final editing phase. Expected completion in 2 weeks."
            },
            {
                "author_id": user_ids[1],
                "book_id": "book_002", 
                "title": "Future Technologies",
                "status": "published",
                "stage_notes": "Successfully published last month. Available on major platforms."
            }
        ]
        
        for book_data in mock_books:
            existing_book = db.books.find_one({"author_id": book_data["author_id"]})
            if not existing_book:
                db.books.insert_one(book_data)
                logger.info(f"Created mock book: {book_data['title']}")
            else:
                logger.info(f"Mock book already exists for author: {book_data['author_id']}")
        
        # Mock Awards
        mock_awards = [
            {
                "author_id": user_ids[0],
                "award_stage": "nominated",
                "award_name": "Tech Innovation Award 2024",
                "eligibility": "Eligible - meets all criteria for emerging technology category"
            },
            {
                "author_id": user_ids[1],
                "award_stage": "winner",
                "award_name": "Best Science Fiction Novel 2023",
                "eligibility": "Winner - recognized for outstanding contribution to science fiction"
            }
        ]
        
        for award_data in mock_awards:
            existing_award = db.awards.find_one({"author_id": award_data["author_id"]})
            if not existing_award:
                db.awards.insert_one(award_data)
                logger.info(f"Created mock award: {award_data['award_name']}")
            else:
                logger.info(f"Mock award already exists for author: {award_data['author_id']}")
        
        logger.info("Mock data seeding completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error seeding mock data: {e}")
        return False

def get_all_users():
    """Get all users (for debugging purposes)."""
    try:
        db = get_database()
        users = list(db.users.find({}, {"password_hash": 0}))  # Exclude password hash
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []
