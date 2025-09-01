#!/usr/bin/env python3
"""
Quick authentication test script.
Tests user registration and login with plain text passwords.

Usage:
    python test_auth.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_authentication():
    """Test user registration and login."""
    print("🔐 Testing Authentication (Plain Text Passwords)")
    print("=" * 50)
    
    # Test user data
    test_user = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    
    try:
        # Test registration
        print("\n📝 Testing User Registration...")
        register_response = requests.post(
            f"{BASE_URL}/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if register_response.status_code == 200:
            print("✅ Registration successful")
            print(f"   Response: {register_response.json()}")
        else:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(f"   Error: {register_response.text}")
            return
        
        # Test login
        print("\n🔑 Testing User Login...")
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        login_response = requests.post(
            f"{BASE_URL}/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            print("✅ Login successful")
            token_data = login_response.json()
            print(f"   Token received: {token_data['access_token'][:50]}...")
            
            # Test protected endpoint
            print("\n🛡️  Testing Protected Endpoint...")
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "Content-Type": "application/json"
            }
            
            profile_response = requests.get(
                f"{BASE_URL}/profile",
                headers=headers
            )
            
            if profile_response.status_code == 200:
                print("✅ Protected endpoint access successful")
                print(f"   Profile: {profile_response.json()}")
            else:
                print(f"❌ Protected endpoint failed: {profile_response.status_code}")
                print(f"   Error: {profile_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
        
        # Test with existing user (alice@example.com)
        print("\n👤 Testing with Existing User...")
        existing_login = {
            "email": "alice@example.com",
            "password": "password123"
        }
        
        alice_response = requests.post(
            f"{BASE_URL}/login",
            json=existing_login,
            headers={"Content-Type": "application/json"}
        )
        
        if alice_response.status_code == 200:
            print("✅ Existing user login successful")
            print(f"   Alice's token: {alice_response.json()['access_token'][:30]}...")
        else:
            print(f"❌ Existing user login failed: {alice_response.status_code}")
            print(f"   Error: {alice_response.text}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the API is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_authentication()
