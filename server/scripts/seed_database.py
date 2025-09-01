#!/usr/bin/env python3
"""
Database seeding script for MongoDB.
Seeds mock users, books, and awards data for development and testing.

Usage:
    python scripts/seed_database.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db_utils import init_database, seed_mock_data
from app.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main seeding function."""
    print("🌱 Starting Database Seeding Process...")
    print(f"📊 Target Database: {settings.MONGO_DB}")
    print(f"🔗 MongoDB URI: {settings.MONGO_URI[:50]}...")
    
    try:
        # Initialize database connection
        print("\n📡 Connecting to MongoDB...")
        if not init_database():
            print("❌ Failed to initialize database connection")
            sys.exit(1)
        
        print("✅ Database connection established")
        
        # Seed mock data
        print("\n🌱 Seeding mock data...")
        if seed_mock_data():
            print("✅ Mock data seeded successfully")
            print("""
📋 Seeded Data Summary:
- 2 mock users (alice@example.com, bob@example.com)  
- 2 mock books with different statuses
- 2 mock awards with different stages
- Password for test users: 'password123'
            """)
        else:
            print("❌ Failed to seed mock data")
            sys.exit(1)
        
        print("🚀 Database seeding completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Seeding interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error during seeding: {e}")
        logger.error(f"Database seeding error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
