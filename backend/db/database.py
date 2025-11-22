from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Build database URL if not provided directly
database_url = settings.database_url
if not database_url and settings.supabase_project_ref and settings.supabase_db_password:
    # Construct Supabase connection pooler URL (recommended)
    if settings.supabase_region:
        database_url = f"postgresql://postgres.{settings.supabase_project_ref}:{settings.supabase_db_password}@aws-0-{settings.supabase_region}.pooler.supabase.com:6543/postgres"
    else:
        # Fallback to direct connection
        database_url = f"postgresql://postgres:{settings.supabase_db_password}@db.{settings.supabase_project_ref}.supabase.co:5432/postgres"

if not database_url:
    raise ValueError(
        "Database URL not configured. Please set DATABASE_URL or Supabase connection parameters in .env"
    )

# Create database engine
# For Supabase connection pooler, use smaller pool sizes
# For direct connection, can use larger pools
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,  # Smaller pool for Supabase connection pooler
    max_overflow=10,
    connect_args={
        "sslmode": "require"  # Supabase requires SSL
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

