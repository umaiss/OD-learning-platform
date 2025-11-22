from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Database Configuration (Supabase)
    # Use Supabase connection pooler URL (recommended for applications)
    # Format: postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
    # Or direct connection: postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
    database_url: str = ""
    
    # Alternative: Individual Supabase connection parameters (if not using full URL)
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None  # Service role key (for server-side operations)
    supabase_db_password: Optional[str] = None
    supabase_project_ref: Optional[str] = None
    supabase_region: Optional[str] = None
    
    # Vector Database
    vector_dimension: int = 1536
    
    # Application Settings
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file (for backward compatibility)


# Global settings instance
settings = Settings()

