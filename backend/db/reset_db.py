"""
Reset database - Drops all tables and recreates them
WARNING: This will delete all data!
"""
import sys
from pathlib import Path

# Add parent directory to path to allow imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import inspect, text
from db.database import engine, Base
from db.models import *
from db.vector import VectorEmbedding, create_vector_extension


def reset_database():
    """Drop all tables and recreate them"""
    print("WARNING: This will delete all data!")
    print("Dropping all tables...")
    
    # Drop all tables with CASCADE to handle foreign key constraints
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        conn.commit()
    
    # Alternative: Drop tables individually with proper order
    # Get all table names
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # Drop tables in reverse dependency order
    for table_name in reversed(tables):
        try:
            with engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not drop table {table_name}: {e}")
    
    print("✓ All tables dropped")
    
    # Create pgvector extension
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
        print("Database reset complete!")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise


if __name__ == "__main__":
    reset_database()

