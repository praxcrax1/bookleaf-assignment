#!/bin/bash

# AI Agent API Setup Script
# This script sets up the development environment and starts the application

set -e  # Exit on any error

echo "🚀 AI Agent API Setup Script"
echo "============================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please run this script from the server directory."
    exit 1
fi

echo "1. Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Found Python $PYTHON_VERSION"

echo "2. Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Created virtual environment"
else
    print_warning "Virtual environment already exists"
fi

echo "3. Activating virtual environment..."
source venv/bin/activate
print_status "Activated virtual environment"

echo "4. Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_status "Installed all dependencies"

echo "5. Checking environment variables..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating template..."
    cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
# Environment Variables - UPDATE THESE VALUES
MONGO_URI=mongodb://localhost:27017
MONGO_DB=ai_agent_db
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=ai-agent-index
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro
JWT_SECRET_KEY=your_super_secret_jwt_key_here_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
    print_warning "Created .env file. Please update it with your API keys before running the application."
else
    print_status "Found existing .env file"
fi

echo "6. Checking MongoDB connection..."
if command -v mongosh &> /dev/null; then
    if mongosh --quiet --eval "db.runCommand('ping')" > /dev/null 2>&1; then
        print_status "MongoDB is running and accessible"
    else
        print_warning "MongoDB is installed but not running. Please start MongoDB service."
    fi
elif command -v mongo &> /dev/null; then
    if mongo --quiet --eval "db.runCommand('ping')" > /dev/null 2>&1; then
        print_status "MongoDB is running and accessible"
    else
        print_warning "MongoDB is installed but not running. Please start MongoDB service."
    fi
else
    print_warning "MongoDB client not found. Please install MongoDB."
    echo "  - Ubuntu/Debian: sudo apt-get install mongodb"
    echo "  - macOS: brew install mongodb-community"
    echo "  - Or use MongoDB Atlas (cloud)"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with real API keys:"
echo "   - Get Pinecone API key from: https://www.pinecone.io/"
echo "   - Get OpenAI API key from: https://platform.openai.com/"
echo "   - Or get Gemini API key from: https://makersuite.google.com/"
echo ""
echo "2. Start the application:"
echo "   ./run.sh"
echo ""
echo "3. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
