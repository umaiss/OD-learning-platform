# Learning Platform Backend API

FastAPI backend for the Learning Platform application with LangChain integration, Supabase database, and PGVector support.

## Features

- **AI Agents**: Skill profiling, learning path generation, content generation, missions, and chatbot
- **Database**: Supabase (PostgreSQL) with SQLAlchemy ORM and PGVector for embeddings
- **Vector Search**: Semantic search using Ollama embeddings for context-aware chatbot responses
- **LLM Integration**: Support for Ollama (local) and OpenAI/Anthropic models via LangChain
- **RESTful API**: Complete CRUD operations for all entities

## Requirements

- Python 3.10+
- Supabase account (free tier available)
- API keys for OpenAI and/or Anthropic

## Setup

1. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up Supabase**:
   - Create a free account at [supabase.com](https://supabase.com)
   - Create a new project
   - Go to **Settings > Database**
   - Enable the `pgvector` extension:
     - Go to **Database > Extensions** in Supabase dashboard
     - Search for "vector" and enable it
     - Or run in SQL Editor: `CREATE EXTENSION IF NOT EXISTS vector;`
   - Get your connection string:
     - Go to **Settings > Database > Connection string**
     - **Choose the right connection method:**
       - **Transaction Pooler** (Recommended for FastAPI) - Port 6543
         - Best for: Production applications, high concurrency, serverless
         - Handles many short-lived connections efficiently
         - Use this for your FastAPI backend
       - **Session Pooler** - Port 6543
         - Best for: Applications needing session-level features (prepared statements, temp tables)
         - Use if you need session-specific functionality
       - **Direct Connection** - Port 5432
         - Best for: One-time operations, migrations, admin tasks
         - Use only for `db/init_db.py` or database migrations
         - NOT recommended for application connections (can exhaust connection limits)
     - Copy the connection string from your chosen method

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration:
# - DATABASE_URL: Your Supabase connection pooler URL
# - OpenAI and/or Anthropic API keys
```

6. **Initialize the database**:
```bash
python db/init_db.py
```

## Running the Server

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

All endpoints are prefixed with `/api/v1`:

### Skill Profile
- `POST /api/v1/skill-profile/assess` - Assess user skills
- `POST /api/v1/skill-profile/` - Create skill profile
- `GET /api/v1/skill-profile/user/{user_id}` - Get user skill profiles
- `GET /api/v1/skill-profile/{profile_id}` - Get skill profile
- `PUT /api/v1/skill-profile/{profile_id}` - Update skill profile
- `DELETE /api/v1/skill-profile/{profile_id}` - Delete skill profile

### Learning Path
- `POST /api/v1/learning-path/generate` - Generate learning path
- `POST /api/v1/learning-path/` - Create learning path
- `GET /api/v1/learning-path/user/{user_id}` - Get user learning paths
- `GET /api/v1/learning-path/{path_id}` - Get learning path
- `PUT /api/v1/learning-path/{path_id}` - Update learning path
- `DELETE /api/v1/learning-path/{path_id}` - Delete learning path

### Content
- `POST /api/v1/content/generate` - Generate learning content
- `POST /api/v1/content/generate-exercise` - Generate exercise
- `POST /api/v1/content/generate-quiz` - Generate quiz
- `POST /api/v1/content/` - Create content
- `GET /api/v1/content/` - List all content
- `GET /api/v1/content/{content_id}` - Get content
- `PUT /api/v1/content/{content_id}` - Update content
- `DELETE /api/v1/content/{content_id}` - Delete content

### Missions
- `POST /api/v1/missions/generate` - Generate mission
- `POST /api/v1/missions/evaluate` - Evaluate mission completion
- `POST /api/v1/missions/` - Create mission
- `GET /api/v1/missions/user/{user_id}` - Get user missions
- `GET /api/v1/missions/{mission_id}` - Get mission
- `PUT /api/v1/missions/{mission_id}` - Update mission
- `PATCH /api/v1/missions/{mission_id}/complete` - Complete mission
- `DELETE /api/v1/missions/{mission_id}` - Delete mission

### Chatbot
- `POST /api/v1/chatbot/chat` - Chat with assistant
- `POST /api/v1/chatbot/answer` - Get detailed answer
- `POST /api/v1/chatbot/hint` - Get hint for problem

### Progress
- `POST /api/v1/progress/` - Create progress record
- `GET /api/v1/progress/user/{user_id}` - Get user progress
- `GET /api/v1/progress/user/{user_id}/entity/{entity_type}/{entity_id}` - Get entity progress
- `PUT /api/v1/progress/{progress_id}` - Update progress
- `PATCH /api/v1/progress/user/{user_id}/entity/{entity_type}/{entity_id}` - Upsert progress
- `GET /api/v1/progress/user/{user_id}/stats` - Get user statistics
- `DELETE /api/v1/progress/{progress_id}` - Delete progress

## Project Structure

```
backend/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── db/
│   ├── __init__.py
│   ├── database.py        # Database connection and session
│   ├── models.py          # SQLAlchemy models
│   ├── vector.py          # Vector embedding models
│   └── init_db.py         # Database initialization script
├── core/
│   ├── __init__.py
│   ├── config.py          # Configuration and settings
│   └── llm.py             # LLM provider factory
├── agents/
│   ├── __init__.py
│   ├── skill_profiler.py  # Skill assessment agent
│   ├── learning_path.py   # Learning path generator
│   ├── content_generator.py # Content generation agent
│   ├── missions.py        # Mission generator
│   └── chatbot.py         # Chatbot agent
└── routes/
    ├── __init__.py
    ├── skill_profile.py   # Skill profile endpoints
    ├── learning_path.py   # Learning path endpoints
    ├── content.py         # Content endpoints
    ├── missions.py        # Mission endpoints
    ├── chatbot.py         # Chatbot endpoints
    └── progress.py        # Progress tracking endpoints
```

## CORS Configuration

The API is configured to accept requests from `http://localhost:3000` (Next.js default port). Update the `allow_origins` in `main.py` if your frontend runs on a different port.

## Database Models

- **User**: User accounts
- **SkillProfile**: User skill assessments
- **LearningPath**: Personalized learning paths
- **Module**: Learning path modules
- **Content**: Generated learning content
- **Mission**: Gamified learning missions
- **Progress**: Progress tracking records
- **ChatMessage**: Chatbot conversation history
- **VectorEmbedding**: Vector embeddings for semantic search

## Vector Search & Semantic Search

The platform uses **PGVector** for semantic search, enabling the chatbot to provide contextually relevant responses based on stored content.

### How It Works

1. **Embedding Generation**: When content is created (lessons, learning plans, profiles), embeddings are automatically generated using Ollama's `nomic-embed-text` model
2. **Storage**: Embeddings are stored in the `vector_embeddings` table with the original text
3. **Semantic Search**: When users chat with the AI coach, their queries are embedded and matched against stored content using cosine similarity
4. **Context-Aware Responses**: The chatbot uses retrieved content to provide more relevant and accurate answers

### Configuration

- **Embedding Model**: Set `OLLAMA_EMBEDDING_MODEL` in `.env` (default: `nomic-embed-text`)
- **Ollama URL**: Set `OLLAMA_BASE_URL` in `.env` (default: `http://localhost:11434`)
- **Vector Dimension**: Set `VECTOR_DIMENSION` in `.env` (default: `768` for nomic-embed-text)

### Requirements

- Ollama must be running locally or accessible at the configured URL
- Install the embedding model: `ollama pull nomic-embed-text`
- pgvector extension must be enabled in Supabase

### Automatic Embedding Creation

Embeddings are automatically created when:
- ✅ Learning content is generated (`/api/v1/content/generate`)
- ✅ Learning paths are generated (`/api/v1/learning-path/generate`)
- ✅ Skill profiles are saved (`/api/v1/profile/save`)

## Development Notes

- All agents use LangChain for LLM interactions
- The LLM provider uses Ollama for local inference (default: `llama3.1`)
- Database models use SQLAlchemy with async support ready
- **Supabase**: Uses connection pooler for better performance (port 6543)
- **PGVector**: Supabase has pgvector extension pre-installed, just enable it in the dashboard
- **Vector Search**: Semantic search is fully integrated and automatically creates embeddings for all generated content
- All endpoints include proper error handling and validation

## Supabase Connection Methods Explained

### For FastAPI Application (Production):
**Use: Transaction Pooler** ✅
- **Port**: 6543
- **Best for**: FastAPI, high concurrency, production workloads
- **Why**: Efficiently handles many short-lived connections, perfect for REST APIs
- **Connection string format**: `postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`

### Alternative (if needed):
**Session Pooler**
- **Port**: 6543
- **Use when**: You need session-level features (prepared statements, temporary tables)
- **Connection string format**: Same as Transaction Pooler (Supabase handles routing)

### For Database Initialization/Migrations:
**Use: Direct Connection**
- **Port**: 5432
- **Best for**: One-time operations like `db/init_db.py`, migrations, admin tasks
- **Why**: Full database access, no pooling overhead
- **Connection string format**: `postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
- **Note**: You can temporarily switch to this for migrations, then switch back to Transaction Pooler

### Quick Setup:
1. **Enable pgvector extension**:
   - Go to Supabase Dashboard > Database > Extensions
   - Search for "vector" and click "Enable"
   - Or run in SQL Editor: `CREATE EXTENSION IF NOT EXISTS vector;`

2. **For your `.env` file**:
   - Use **Transaction Pooler** connection string for `DATABASE_URL`
   - This is what your FastAPI app will use for all operations

