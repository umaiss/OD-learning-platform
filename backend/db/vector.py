from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from db.database import Base
from core.config import settings


class VectorEmbedding(Base):
    """Vector embedding model for semantic search"""
    __tablename__ = "vector_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    # Foreign keys for different content types
    content_id = Column(Integer, ForeignKey("content.id"), nullable=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=True)
    learning_plan_id = Column(Integer, ForeignKey("learning_plans.id"), nullable=True)
    generated_content_id = Column(Integer, ForeignKey("generated_content.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    
    content_type = Column(String, nullable=False, index=True)  
    # Types: content, skill, learning_path, learner, learning_plan, generated_content, lesson_text, course
    
    text = Column(Text, nullable=False)
    embedding = Column(Vector(settings.vector_dimension), nullable=False)
    meta_data = Column(Text)  # JSON string for additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


def create_vector_extension(engine):
    """Create pgvector extension in PostgreSQL"""
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

