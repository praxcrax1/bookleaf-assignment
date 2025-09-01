# AI Agent API - Production-Ready Conversational AI Backend

A sophisticated conversational AI agent that intelligently decides between structured database queries (MongoDB) and semantic document search (Pinecone) to provide comprehensive, context-aware responses.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │────│   FastAPI API    │────│   AI Agent      │
│   (React/Vue)   │    │   (JWT Auth)     │    │  (LangChain)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                       ┌────────┴────────┐              │
                       │                 │              │
                   ┌───▼────┐      ┌────▼─────┐        │
                   │MongoDB │      │ Pinecone │        │
                   │Structured│    │ Vector   │        │
                   │Data      │    │ Search   │        │
                   └────────────┘  └──────────┘        │
                                                       │
                                          ┌────────────▼─────────┐
                                          │  LLM Providers      │
                                          │  (OpenAI/Gemini)    │
                                          └──────────────────────┘
```

## ✨ Features

### 🔐 Authentication & Security
- **JWT Authentication** with secure token management
- **bcrypt Password Hashing** for user credentials
- **Protected Routes** with automatic user context injection
- **CORS Support** for frontend integration

### 🧠 Intelligent Agent System
- **Multi-Source Decision Making**: Automatically chooses between structured DB queries vs semantic search
- **Context-Aware Memory**: Persistent conversation history with MongoDB
- **Tool Selection Logic**: Smart reasoning about when to use different data sources
- **Error Handling**: Graceful degradation with helpful error messages

### 🔍 Dual Data Architecture
- **MongoDB (Structured)**: User profiles, book status, awards, chat histories
- **Pinecone (Unstructured)**: FAQ documents, notes, semantic knowledge base
- **Smart Filtering**: All queries automatically filter by user_id for privacy

### 🛠️ Production-Ready Features
- **Health Monitoring**: Comprehensive health checks for all services
- **Logging**: Structured logging throughout the application
- **Mock Data**: Automatic seeding for development/testing
- **Modular Design**: Clean separation of concerns across modules
- **Error Recovery**: Fallback mechanisms for service failures

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB (local or cloud)
- Pinecone account
- OpenAI API key or Google Gemini API key

### 1. Installation

```bash
# Clone the repository
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env` file and update with your credentials:

```env
# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB=ai_agent_db

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=ai-agent-index

# LLM Providers
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro

# JWT Security
JWT_SECRET_KEY=your_super_secret_jwt_key_here_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Seed Data (First Time Setup)

Before running the application for the first time, seed the databases with sample data:

```bash
# Run all seeding operations (recommended)
python scripts/seed_all.py

# Or run individual seeding scripts:
python scripts/seed_database.py    # MongoDB mock data
python scripts/seed_pinecone.py    # Company FAQ documents
```

This will create:
- **Mock Users**: `alice@example.com` and `bob@example.com` (password: `password123`)
- **Sample Books**: Different publishing stages and statuses
- **Sample Awards**: Various award stages and eligibility statuses  
- **Company FAQs**: Knowledge base accessible to all users

### 4. Run the Application

```bash
# Start the FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com", 
  "password": "secure_password"
}
```

#### Login
```http
POST /login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Protected Chat Endpoint

```http
POST /chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "query": "What's the status of my book?",
  "doc_ids": ["doc_1", "doc_2"],  // Optional: search specific docs
  "verbose": true  // Optional: include reasoning steps
}
```

Response:
```json
{
  "answer": "Your book 'The Digital Revolution' is currently in the editing stage...",
  "user_id": "user_123",
  "query": "What's the status of my book?",
  "reasoning_steps": [...],  // If verbose=true
  "success": true
}
```

### Other Endpoints

- `GET /health` - System health check
- `GET /profile` - User profile information
- `GET /` - API information

## 🧩 System Components

### Agent Intelligence (`app/agent.py`)
- **Multi-step Reasoning**: Allows up to 5 reasoning iterations
- **Tool Selection**: Intelligent decision making between tools:
  - `search_documents`: Semantic search for FAQs and general knowledge
  - `book_status_lookup`: Structured queries for manuscript status
  - `award_status_lookup`: Structured queries for awards/nominations
  - `get_user_profile_summary`: Comprehensive user overview

### Database Layer (`app/db_utils.py`)
- **User Management**: Registration, authentication, profile management
- **Mock Data Seeding**: Automatic creation of test users, books, and awards
- **Query Functions**: Optimized database queries with proper indexing

### Vector Search (`app/pinecone_utils.py`)
- **Document Embedding**: Automatic text-to-vector conversion using OpenAI embeddings
- **Semantic Search**: Similarity-based document retrieval with configurable thresholds
- **User Isolation**: All searches filtered by user_id for privacy

### Authentication (`app/auth.py`)
- **Secure Registration**: Password hashing with bcrypt
- **JWT Token Management**: Secure token creation and validation
- **Protected Routes**: Automatic user authentication for sensitive endpoints

## 🔧 Configuration Options

### LLM Providers
The system supports both OpenAI and Google Gemini:

```python
# In agent.py, change llm_provider parameter
agent = create_agent(user_id="user_123", llm_provider="openai")  # or "gemini"
```

### Similarity Thresholds
Adjust semantic search sensitivity:

```python
# In pinecone_utils.py
search_results = search_documents(
    query="example",
    user_id="user_123",
    min_similarity=0.7  # Adjust threshold (0.0-1.0)
)
```

### Memory Configuration
The system uses MongoDB for persistent chat history. Memory can be configured in `agent.py`.

## 🔍 Example Interactions

### Book Status Query
**User**: "How's my book coming along?"

**System Reasoning**:
1. Identifies as status query → uses `book_status_lookup`
2. Retrieves structured data from MongoDB
3. Provides detailed status with editorial notes

### FAQ Query
**User**: "How long does editing usually take?"

**System Reasoning**:
1. Identifies as general knowledge query → uses `search_documents`
2. Searches FAQ documents in Pinecone
3. Returns semantic matches with similarity scores

### Complex Query
**User**: "What's my current situation with everything?"

**System Reasoning**:
1. Identifies as overview query → uses `get_user_profile_summary`
2. Combines book status + award status
3. May also search documents for additional context

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   ```bash
   # Check if MongoDB is running
   mongosh  # Should connect successfully
   ```

2. **Pinecone API Errors**
   - Verify API key and environment in `.env`
   - Check if index exists in Pinecone dashboard

3. **LLM API Errors**
   - Verify OpenAI/Gemini API keys
   - Check API quotas and billing

4. **JWT Token Issues**
   - Ensure JWT_SECRET_KEY is set and secure
   - Token expires after 30 minutes by default

### Debug Mode
Enable verbose logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🚢 Deployment

### Docker Deployment (Recommended)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
```bash
# Use strong JWT secret
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Use production MongoDB URI
MONGO_URI=mongodb://username:password@your-mongo-cluster

# Set appropriate CORS origins
CORS_ORIGINS=https://yourdomain.com
```

## 📈 Performance Optimization

### Database Indexes
The system automatically creates indexes for:
- `users.email` (unique)
- `books.author_id`
- `awards.author_id`

### Pinecone Configuration
- Uses `text-embedding-ada-002` (1536 dimensions)
- Cosine similarity metric
- Serverless index for cost optimization

### Caching (Future Enhancement)
Consider adding Redis caching for:
- Frequently accessed user profiles
- Popular document searches
- JWT token validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with proper documentation
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs for detailed error messages
3. Create an issue with full error details and environment info

---

**Built with ❤️ using FastAPI, LangChain, MongoDB, and Pinecone**
