#!/usr/bin/env python3

"""
Test script for AI Agent API
Tests all endpoints and basic functionality
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpassword123"
}

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        
    def print_success(self, message: str):
        print(f"✅ {message}")
        
    def print_error(self, message: str):
        print(f"❌ {message}")
        
    def print_info(self, message: str):
        print(f"ℹ️  {message}")
        
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper error handling."""
        url = f"{self.base_url}{endpoint}"
        
        # Add authorization header if token is available
        if self.access_token and 'headers' not in kwargs:
            kwargs['headers'] = {}
        
        if self.access_token:
            kwargs['headers']['Authorization'] = f"Bearer {self.access_token}"
            
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed. Is the server running at {self.base_url}?")
            sys.exit(1)
    
    def test_health_check(self) -> bool:
        """Test the health check endpoint."""
        self.print_info("Testing health check...")
        
        response = self.make_request("GET", "/health")
        
        if response.status_code == 200:
            data = response.json()
            self.print_success(f"Health check passed: {data.get('status')}")
            if data.get('database_connected'):
                self.print_success("Database connection: OK")
            else:
                self.print_error("Database connection: FAILED")
            
            if data.get('pinecone_connected'):
                self.print_success("Pinecone connection: OK")
            else:
                self.print_error("Pinecone connection: FAILED")
            return True
        else:
            self.print_error(f"Health check failed: {response.status_code}")
            return False
    
    def test_registration(self) -> bool:
        """Test user registration."""
        self.print_info("Testing user registration...")
        
        response = self.make_request(
            "POST", 
            "/register",
            json=TEST_USER
        )
        
        if response.status_code == 200:
            data = response.json()
            self.print_success(f"Registration successful: {data.get('message')}")
            return True
        elif response.status_code == 400:
            data = response.json()
            if "already registered" in data.get("detail", "").lower():
                self.print_info("User already exists (this is fine for testing)")
                return True
            else:
                self.print_error(f"Registration failed: {data.get('detail')}")
                return False
        else:
            self.print_error(f"Registration failed: {response.status_code} - {response.text}")
            return False
    
    def test_login(self) -> bool:
        """Test user login and store token."""
        self.print_info("Testing user login...")
        
        response = self.make_request(
            "POST",
            "/login", 
            json={"email": TEST_USER["email"], "password": TEST_USER["password"]}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.print_success("Login successful, token received")
            return True
        else:
            self.print_error(f"Login failed: {response.status_code} - {response.text}")
            return False
    
    def test_profile(self) -> bool:
        """Test protected profile endpoint."""
        self.print_info("Testing profile endpoint...")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
            
        response = self.make_request("GET", "/profile")
        
        if response.status_code == 200:
            data = response.json()
            self.print_success(f"Profile retrieved: {data.get('name')} ({data.get('email')})")
            return True
        else:
            self.print_error(f"Profile request failed: {response.status_code} - {response.text}")
            return False
    
    def test_chat(self) -> bool:
        """Test the chat endpoint."""
        self.print_info("Testing chat endpoint...")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
        
        # Test different types of queries
        test_queries = [
            {
                "query": "Hello, can you help me?",
                "description": "Basic greeting"
            },
            {
                "query": "What's the status of my book?",
                "description": "Book status query"
            },
            {
                "query": "Do I have any awards?",
                "description": "Award status query"
            },
            {
                "query": "How long does editing usually take?",
                "description": "FAQ-style query"
            }
        ]
        
        success_count = 0
        
        for test in test_queries:
            self.print_info(f"Testing: {test['description']}")
            
            response = self.make_request(
                "POST",
                "/chat",
                json={"query": test["query"], "verbose": True}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.print_success(f"Chat response: {data.get('answer')[:100]}...")
                    success_count += 1
                else:
                    self.print_error(f"Chat failed: {data.get('answer')}")
            else:
                self.print_error(f"Chat request failed: {response.status_code} - {response.text}")
            
            time.sleep(1)  # Brief pause between requests
        
        return success_count > 0
    
    def test_root_endpoint(self) -> bool:
        """Test the root endpoint."""
        self.print_info("Testing root endpoint...")
        
        response = self.make_request("GET", "/")
        
        if response.status_code == 200:
            data = response.json()
            self.print_success(f"Root endpoint: {data.get('message')}")
            return True
        else:
            self.print_error(f"Root endpoint failed: {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Run all API tests."""
        print("🧪 AI Agent API Test Suite")
        print("=" * 50)
        
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_registration),
            ("User Login", self.test_login),
            ("User Profile", self.test_profile),
            ("Chat Functionality", self.test_chat),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 30)
            
            try:
                success = test_func()
                results.append((test_name, success))
                
                if success:
                    self.print_success(f"{test_name} passed")
                else:
                    self.print_error(f"{test_name} failed")
                    
            except Exception as e:
                self.print_error(f"{test_name} error: {str(e)}")
                results.append((test_name, False))
            
            time.sleep(1)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! The API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
            return False

def main():
    """Main function."""
    print("🚀 Starting API tests...")
    print("Make sure the server is running on localhost:8000\n")
    
    tester = APITester(BASE_URL)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
