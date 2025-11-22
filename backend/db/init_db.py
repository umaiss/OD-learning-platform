"""
Database initialization script
Run this to create all tables and extensions
"""
import sys
from pathlib import Path

# Add parent directory to path to allow imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from db.database import engine, Base
from db.models import *
from db.vector import VectorEmbedding, create_vector_extension


def init_database():
    """Initialize database with all tables and extensions"""
    # Create pgvector extension (if not already enabled)
    try:
        create_vector_extension(engine)
        print("✓ pgvector extension created/enabled")
    except Exception as e:
        print(f"⚠ Warning: Could not create pgvector extension: {e}")
        print("  For Supabase: Enable pgvector in Dashboard > Database > Extensions")
        print("  Or it may already be enabled. Continuing with table creation...")
    
    # Create all tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ All database tables created")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise


if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialization complete!")

