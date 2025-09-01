#!/usr/bin/env python3
"""
Pinecone seeding script for company FAQ documents.
Seeds company FAQ documents that are accessible to all users.

Usage:
    python scripts/seed_pinecone.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.pinecone_utils import init_pinecone, seed_company_faq_documents, get_total_faq_count
from app.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main seeding function."""
    print("🌱 Starting Pinecone FAQ Seeding Process...")
    print(f"📊 Target Index: {settings.PINECONE_INDEX_NAME}")
    print(f"🔗 Pinecone Environment: {settings.PINECONE_ENVIRONMENT}")
    
    try:
        # Initialize Pinecone connection
        print("\n📡 Connecting to Pinecone...")
        if not init_pinecone():
            print("❌ Failed to initialize Pinecone connection")
            sys.exit(1)
        
        print("✅ Pinecone connection established")
        
        # Check current FAQ count
        current_count = get_total_faq_count()
        print(f"📄 Current FAQ documents: {current_count}")
        
        # Seed FAQ documents
        print("\n🌱 Seeding company FAQ documents...")
        if seed_company_faq_documents():
            new_count = get_total_faq_count()
            print("✅ Company FAQ documents seeded successfully")
            print(f"""
📋 Seeded FAQ Summary:
- Total FAQ documents: {new_count}
- Documents added: {new_count - current_count}
- Topics covered: Book Status, Awards, Publishing Process
- Accessibility: All users (no user filtering)

🔍 FAQ Categories:
- Book Status & Manuscript Tracking
- Award Eligibility & Submission
- Publishing Process & Timelines
            """)
        else:
            print("❌ Failed to seed FAQ documents")
            sys.exit(1)
        
        print("🚀 Pinecone FAQ seeding completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Seeding interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error during seeding: {e}")
        logger.error(f"Pinecone seeding error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
