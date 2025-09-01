#!/usr/bin/env python3
"""
Master seeding script that seeds both MongoDB and Pinecone.
Runs database seeding first, then Pinecone FAQ seeding.

Usage:
    python scripts/seed_all.py
"""

import sys
import os
import subprocess

def run_script(script_name, description):
    """Run a Python script and handle errors."""
    print(f"\n🚀 Running {description}...")
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), script_name)
        ], check=True, capture_output=True, text=True)
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with return code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    """Main function to run all seeding scripts."""
    print("🌟 Starting Complete Data Seeding Process...")
    print("=" * 60)
    
    success_count = 0
    total_scripts = 2
    
    # Seed database first
    if run_script("seed_database.py", "Database Seeding"):
        success_count += 1
        print("✅ Database seeding completed")
    else:
        print("❌ Database seeding failed")
    
    # Add a small delay between operations
    import time
    time.sleep(2)
    
    # Seed Pinecone FAQs
    if run_script("seed_pinecone.py", "Pinecone FAQ Seeding"):
        success_count += 1
        print("✅ Pinecone FAQ seeding completed")
    else:
        print("❌ Pinecone FAQ seeding failed")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Seeding Summary: {success_count}/{total_scripts} scripts completed successfully")
    
    if success_count == total_scripts:
        print("🎉 All seeding operations completed successfully!")
        print("""
🚀 Your AI Agent is now ready with:
- Mock user accounts for testing
- Sample book and award data
- Company FAQ documents for semantic search

📝 Test Credentials:
- Email: alice@example.com or bob@example.com
- Password: password123
        """)
    else:
        print("⚠️  Some seeding operations failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Seeding process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
