"""
Agent creation logic for conversational AI with document search and MongoDB-backed memory.
Creates intelligent agents that can reason about when to use different tools and data sources.
"""
from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from app.core.tools import search_faq_documents, book_status_lookup, award_status_lookup, get_user_profile_summary
from app.config import settings
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging

logger = logging.getLogger(__name__)

def create_agent(user_id=None, doc_ids=None, llm_provider="gemini"):
    """
    Create a conversational AI agent with access to multiple data sources and reasoning capabilities.
    
    The agent can intelligently decide when to:
    - Search semantic documents (Pinecone) for FAQ-style queries
    - Query structured data (MongoDB) for specific book/award status
    - Combine multiple sources for comprehensive answers
    
    Args:
        user_id: ID of the user for personalized responses and data filtering
        doc_ids: Optional list of specific document IDs to search within
        llm_provider: LLM provider to use ("gemini" or "openai")
        
    Returns:
        AgentExecutor: Configured agent ready for conversation
    """
    try:
        # Initialize the language model based on provider
        if llm_provider.lower() == "openai":
            model = ChatOpenAI(
                model="gpt-4",
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.3
            )
            logger.info("Using OpenAI GPT-4 model")
        else:
            model = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.3
            )
            logger.info(f"Using Google Gemini model: {settings.GEMINI_MODEL}")

        # Tool wrapper functions to inject user_id
        def search_faq_user(query: str):
            """Search company FAQ documents (no user_id needed)."""
            return search_faq_documents.invoke({"query": query})

        def book_status_user(author_id: str = None):
            """Look up book status with automatic user_id injection."""
            inputs = {"user_id": user_id}
            if author_id:
                inputs["author_id"] = author_id
            return book_status_lookup.invoke(inputs)

        def award_status_user(author_id: str = None):
            """Look up award status with automatic user_id injection."""
            inputs = {"user_id": user_id}
            if author_id:
                inputs["author_id"] = author_id
            return award_status_lookup.invoke(inputs)

        def profile_summary_user():
            """Get user profile summary with automatic user_id injection."""
            return get_user_profile_summary.invoke({"user_id": user_id})

        # Define tools available to the agent
        tools = [
            Tool(
                name="search_faq_documents",
                func=search_faq_user,
                description=(
                    "Search through company FAQ documents using semantic similarity. "
                    "Use this for general information queries about company processes, "
                    "publishing guidelines, award requirements, and other FAQ topics. "
                    "Most effective for explanatory content and general knowledge questions."
                )
            ),
            Tool(
                name="book_status_lookup",
                func=book_status_user,
                description=(
                    "Look up current book status, manuscript stage, and editorial notes. "
                    "Use this when user asks about their book progress, editing status, "
                    "publication timeline, or manuscript-related questions. "
                    "Provides structured information from the publishing database."
                )
            ),
            Tool(
                name="award_status_lookup", 
                func=award_status_user,
                description=(
                    "Look up award nominations, eligibility status, and recognition details. "
                    "Use this when user asks about awards, nominations, competitions, "
                    "or recognition status. Provides structured information from awards database."
                )
            ),
            Tool(
                name="get_user_profile_summary",
                func=profile_summary_user,
                description=(
                    "Get a comprehensive overview of user's profile including books and awards. "
                    "Use this when user wants a general overview, dashboard view, "
                    "or summary of their current status across all areas."
                )
            )
        ]

        # Bind tools to the model
        llm_with_tools = model.bind_tools(tools)

        # Set up MongoDB-backed conversation memory for persistent chat history
        try:
            message_history = MongoDBChatMessageHistory(
                connection_string=settings.MONGO_URI,
                session_id=str(user_id) if user_id else "anonymous",
                database_name=settings.MONGO_DB,
                collection_name="chat_histories"
            )

            memory = ConversationBufferMemory(
                chat_memory=message_history,
                memory_key="chat_history",
                return_messages=True
            )
            logger.info(f"Initialized MongoDB chat memory for user {user_id}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize MongoDB memory, using in-memory fallback: {e}")
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )

        # Advanced prompt template for intelligent reasoning and tool selection
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                f"""You are an advanced AI assistant specializing in helping authors and writers manage their work. You have access to both structured data (book/award status) and company FAQ documents.

**CORE DECISION FRAMEWORK:**

1. **ANALYZE THE QUERY TYPE:**
   - **Status Questions** ("What's my book status?", "How's my manuscript?") → Use `book_status_lookup`
   - **Award Questions** ("Am I nominated?", "Award eligibility?") → Use `award_status_lookup`  
   - **General/FAQ Questions** ("How does editing work?", "What are requirements?") → Use `search_faq_documents`
   - **Overview Questions** ("Show me everything", "What's my profile?") → Use `get_user_profile_summary`

2. **INTELLIGENT TOOL USAGE:**
   - **Company FAQ Search:** Use for general information about processes, requirements, timelines
   - **Multi-source queries:** Combine tools intelligently (e.g., get book status + search for editing process info)
   - **Follow-up searches:** If initial search doesn't answer completely, try different search terms
   - **Structured + FAQ:** Use both MongoDB lookups and FAQ search for comprehensive answers

3. **QUALITY STANDARDS:**
   - **Honesty Principle:** If similarity score < 0.7 or no relevant info found, say "I don't know about this"
   - **Step-by-step reasoning:** Always explain your thought process
   - **User-specific data:** Book/award lookups are automatically filtered by user_id for privacy
   - **Comprehensive responses:** Don't just return raw data - analyze and explain

4. **RESPONSE FORMATTING:**
   - Use clear Markdown formatting with headers and bullet points
   - Distinguish between database information and FAQ content  
   - Provide actionable insights when possible
   - If information is incomplete, suggest how user can get more details

5. **MEMORY UTILIZATION:**
   - Reference previous conversations when relevant
   - Build context over multiple interactions
   - Remember user preferences and past questions

**ERROR HANDLING:**
- If a tool fails, try alternative approaches
- If no information is found, be honest and suggest alternatives
- Always maintain a helpful tone even when information is limited

**CONVERSATION STYLE:**
- Professional yet friendly
- Focus on being genuinely helpful
- Provide specific, actionable information
- Ask clarifying questions when needed

Remember: You're not just retrieving information - you're intelligently reasoning about what the user needs and providing the most helpful response possible.
"""
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])

        # Create the agent with tool calling capability
        agent = create_tool_calling_agent(llm_with_tools, tools, prompt=prompt)
        
        # Build and return the agent executor with enhanced capabilities
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=5,  # Allow multiple reasoning steps
            early_stopping_method="generate",  # Continue until a good answer is found
            handle_parsing_errors=True  # Gracefully handle parsing errors
        )

        logger.info(f"Successfully created agent for user {user_id}")
        return agent_executor

    except Exception as e:
        logger.error(f"Error creating agent for user {user_id}: {e}")
        raise

def create_simple_agent(user_id=None):
    """
    Create a simpler version of the agent for fallback scenarios.
    
    Args:
        user_id: ID of the user
        
    Returns:
        AgentExecutor: Basic agent with limited functionality
    """
    try:
        # Use a simpler model setup
        model = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1
        )

        # Minimal toolset
        def search_faq_simple(query: str):
            """Simple FAQ search function."""
            return search_faq_documents.invoke({"query": query})

        tools = [
            Tool(
                name="search_faq_documents",
                func=search_faq_simple,
                description="Search company FAQ documents for relevant information."
            )
        ]

        llm_with_tools = model.bind_tools(tools)

        # Simple prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Use the search tool to find relevant information when needed."),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])

        agent = create_tool_calling_agent(llm_with_tools, tools, prompt=prompt)
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            max_iterations=2
        )

        logger.info(f"Created simple fallback agent for user {user_id}")
        return agent_executor

    except Exception as e:
        logger.error(f"Error creating simple agent: {e}")
        raise
