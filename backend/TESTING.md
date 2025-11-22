# Backend Testing Guide

Complete guide for running and testing the Learning Platform backend.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Running the Server](#running-the-server)
4. [Testing API Endpoints](#testing-api-endpoints)
5. [Running Tests](#running-tests)
6. [Seed Data](#seed-data)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.10+
- Supabase account (free tier available)
- Ollama installed and running (for LLM agents)
- PostgreSQL client (optional, for direct database access)

## Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database (Supabase)
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# Ollama (for LLM agents)
OLLAMA_MODEL=llama3.1

# API Configuration
API_V1_PREFIX=/api/v1
ENVIRONMENT=development
DEBUG=true
```

### 3. Initialize Database

**Important**: Use the venv's Python directly to avoid import issues:

```bash
# Option 1: Use venv's Python directly (recommended)
./venv/bin/python db/init_db.py

# Option 2: Activate venv first, then use python
source venv/bin/activate
python db/init_db.py
```

This will:
- Create all database tables
- Enable pgvector extension (if using Supabase, enable it in the dashboard first)

### 4. Seed Demo Data (Optional)

**Important**: Make sure the database is initialized first (step 3).

```bash
# Make sure you're using the venv's Python
./venv/bin/python seeds/seed_data.py

# Or activate venv first
source venv/bin/activate
python seeds/seed_data.py
```

This creates:
- 1 demo learner with sample skill map
- Sample progress record

## Running the Server

### Development Mode (with auto-reload)

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Using a Different Port

```bash
uvicorn main:app --reload --port 8080
```

## Testing API Endpoints

### API Documentation

Once the server is running, access interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "learning-platform-api"
}
```

### Using cURL

#### 1. Generate Skill Profile

```bash
curl -X POST "http://localhost:8000/api/v1/profile/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "learner_id": 1,
    "self_assessment": "I am good at Python and React, but need to learn Docker and Kubernetes.",
    "role": "software engineer",
    "experience": 3
  }'
```

#### 2. Generate Learning Path

```bash
curl -X POST "http://localhost:8000/api/v1/learning-path/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "learner_id": 1,
    "skill_map": {
      "Python": "intermediate",
      "Docker": "beginner",
      "Kubernetes": "beginner"
    },
    "experience": 3,
    "role": "software engineer"
  }'
```

#### 3. Generate Content

```bash
curl -X POST "http://localhost:8000/api/v1/content/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "learner_id": 1,
    "module_name": "Docker Basics"
  }'
```

#### 4. Generate Daily Missions

```bash
curl -X POST "http://localhost:8000/api/v1/missions/daily" \
  -H "Content-Type: application/json" \
  -d '{
    "learner_id": 1,
    "skill_map": {
      "Python": "intermediate",
      "Docker": "beginner"
    }
  }'
```

#### 5. Update Progress

```bash
curl -X POST "http://localhost:8000/api/v1/progress/update" \
  -H "Content-Type: application/json" \
  -d '{
    "learner_id": 1,
    "completed_modules": ["Docker Basics"],
    "xp": 50,
    "streak": 1
  }'
```

#### 6. Chat with Bot

```bash
curl -X POST "http://localhost:8000/api/v1/chatbot/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "learner_id": 1,
    "message": "How do I get started with Docker?",
    "conversation_history": []
  }'
```

### Using Python Requests

Create a test script `test_api.py`:

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Generate profile
response = requests.post(
    f"{BASE_URL}/profile/generate",
    json={
        "learner_id": 1,
        "self_assessment": "I know Python well, but new to Docker.",
        "role": "developer",
        "experience": 2
    }
)
print("Profile:", response.json())

# Generate learning path
response = requests.post(
    f"{BASE_URL}/learning-path/generate",
    json={
        "learner_id": 1,
        "skill_map": {"Python": "intermediate", "Docker": "beginner"},
        "experience": 2,
        "role": "developer"
    }
)
print("Learning Path:", response.json())
```

Run it:
```bash
python test_api.py
```

## Running Tests

### Prerequisites for Tests

1. **Ollama must be running**:
   ```bash
   ollama serve
   ```

2. **Model must be available**:
   ```bash
   ollama pull llama3.1
   ```

3. **Environment variable set** (or use default):
   ```bash
   export OLLAMA_MODEL=llama3.1
   ```

### Run All Tests

```bash
cd backend
source venv/bin/activate
pytest tests/test_agents.py -v
```

### Run Specific Test

```bash
# Test skill profiler
pytest tests/test_agents.py::test_skill_profiler_generate_skill_profile -v

# Test learning path generator
pytest tests/test_agents.py::test_learning_path_generator_generate_learning_path_plan -v

# Test content generator
pytest tests/test_agents.py::test_content_generator_generate_content -v
```

### Run Tests with Coverage

```bash
pip install pytest-cov
pytest tests/test_agents.py --cov=agents --cov-report=html
```

### Test Output

Expected output:
```
tests/test_agents.py::test_skill_profiler_generate_skill_profile PASSED
tests/test_agents.py::test_learning_path_generator_generate_learning_path_plan PASSED
tests/test_agents.py::test_content_generator_generate_content PASSED
tests/test_agents.py::test_mission_generator_generate_daily_missions PASSED
tests/test_agents.py::test_chatbot_agent_chat_with_context PASSED
...
```

## Seed Data

### Create Demo Data

**Prerequisites**: Database must be initialized first (`python db/init_db.py`)

```bash
cd backend
source venv/bin/activate

# Make sure database is initialized
python db/init_db.py

# Then seed data
python seeds/seed_data.py
```

**Note**: If you get `ModuleNotFoundError`, use the venv's Python directly:
```bash
./venv/bin/python seeds/seed_data.py
```

### Output

```
Starting database seeding...
==================================================

1. Creating demo learner...
   Name: Demo Learner
   Role: software engineer
   Experience: 3 years
   Skills: 10 skills mapped

   Skill Map:
     - Python: intermediate
     - JavaScript: advanced
     - React: intermediate
     ...

2. Creating sample progress...
   Completed modules: 4
   Total XP: 250
   Current streak: 7 days

==================================================
Database seeding completed successfully!

Demo Learner ID: 1
Progress Record ID: 1
```

### Use Demo Learner ID

After seeding, use `learner_id: 1` in your API calls:

```bash
curl -X POST "http://localhost:8000/api/v1/profile/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "learner_id": 1,
    ...
  }'
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Problem**: `ModuleNotFoundError: No module named 'sqlalchemy'`

**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database Connection Error

**Problem**: `could not translate host name`

**Solution**:
1. Check your `.env` file has correct `DATABASE_URL`
2. Verify Supabase project is active
3. Use Transaction Pooler connection string (port 6543)

### Issue: Ollama Not Found

**Problem**: `OllamaEndpointNotFoundError` or `Connection refused`

**Solution**:
```bash
# Start Ollama
ollama serve

# In another terminal, verify it's running
ollama list

# Pull the model if needed
ollama pull llama3.1
```

### Issue: Tests Failing

**Problem**: Tests fail with validation errors

**Solution**:
1. Ensure Ollama is running: `ollama serve`
2. Verify model is available: `ollama list`
3. Check `OLLAMA_MODEL` environment variable
4. Some tests may fail if LLM output doesn't match schema exactly (this is expected with LLMs)

### Issue: Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Use a different port
uvicorn main:app --reload --port 8080

# Or find and kill the process using port 8000
lsof -ti:8000 | xargs kill
```

### Issue: CORS Errors

**Problem**: CORS errors when calling from frontend

**Solution**:
Update `main.py` to include your frontend URL:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Add your frontend URL
    ...
)
```

## Quick Start Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` file with database URL
- [ ] Initialize database: `./venv/bin/python db/init_db.py` (or use `./run.sh init-db`)
- [ ] (Optional) Seed demo data: `./venv/bin/python seeds/seed_data.py` (or use `./run.sh seed`)
- [ ] Start Ollama: `ollama serve` (in a separate terminal)
- [ ] Pull model: `ollama pull llama3.1`
- [ ] Start server: `./venv/bin/uvicorn main:app --reload` (or use `./run.sh server`)
- [ ] Test health: `curl http://localhost:8000/health`
- [ ] View docs: http://localhost:8000/docs
- [ ] Run tests: `./venv/bin/pytest tests/test_agents.py -v` (or use `./run.sh test tests/test_agents.py -v`)

## Helper Script

A helper script `run.sh` is provided to run common commands with the correct Python interpreter:

```bash
# Initialize database
./run.sh init-db

# Seed demo data
./run.sh seed

# Run tests
./run.sh test tests/test_agents.py -v

# Start server
./run.sh server
```

This ensures you're always using the venv's Python, avoiding import errors.

## Next Steps

1. Explore API documentation at http://localhost:8000/docs
2. Test endpoints using the interactive Swagger UI
3. Run the test suite to verify all agents work
4. Use seed data to test with a demo learner
5. Integrate with your frontend application

