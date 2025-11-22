# Agent Tests

Test suite for all agent methods using pytest.

## Setup

1. Install test dependencies:
```bash
pip install pytest pytest-asyncio
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Running Tests

Run all tests:
```bash
pytest tests/test_agents.py
```

Run with verbose output:
```bash
pytest tests/test_agents.py -v
```

Run a specific test:
```bash
pytest tests/test_agents.py::test_skill_profiler_generate_skill_profile -v
```

## Test Coverage

The test suite covers:
- ✅ Skill Profiler: Verifies strengths, gaps, and skill_map output
- ✅ Learning Path Generator: Verifies weekly_goals, milestones, and modules
- ✅ Content Generator: Verifies lesson_text and quiz structure
- ✅ Mission Generator: Verifies missions list, XP, and streak_increment
- ✅ Chatbot Agent: Verifies technical response generation

## Requirements

- Ollama must be running locally
- OLLAMA_MODEL environment variable set (defaults to "llama3.1")
- The specified model must be available in Ollama

## Note

These are integration tests that require Ollama to be running. They will make actual LLM calls, so they may take some time to complete.

