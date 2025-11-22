"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Configure pytest for async tests
pytest_plugins = ('pytest_asyncio',)

