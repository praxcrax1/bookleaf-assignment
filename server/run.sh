#!/bin/bash

# Run script for AI Agent API
# This script activates the virtual environment and starts the FastAPI server

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🚀 Starting AI Agent API..."
echo "=========================="

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please run this script from the server directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Using environment variables or defaults."
fi

# Start the FastAPI application
print_status "Starting FastAPI server on http://localhost:8000"
echo ""
echo "API Documentation will be available at:"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start with uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
