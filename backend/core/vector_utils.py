"""
Utility functions for creating and managing vector embeddings
"""
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from db.vector import VectorEmbedding
from core.embeddings import generate_embedding


async def create_vector_embedding(
    db: Session,
    text: str,
    content_type: str,
    content_id: Optional[int] = None,
    learner_id: Optional[int] = None,
    learning_plan_id: Optional[int] = None,
    generated_content_id: Optional[int] = None,
    meta_data: Optional[Dict[str, Any]] = None
) -> VectorEmbedding:
    """
    Create and save a vector embedding for text content
    
    Args:
        db: Database session
        text: Text content to embed
        content_type: Type of content (e.g., "lesson_text", "learning_plan", "skill_profile")
        content_id: Optional foreign key to content table
        learner_id: Optional foreign key to learners table
        learning_plan_id: Optional foreign key to learning_plans table
        generated_content_id: Optional foreign key to generated_content table
        meta_data: Optional metadata dictionary to store as JSON
        
    Returns:
        VectorEmbedding: Created vector embedding record
    """
    try:
        # Generate embedding
        embedding_vector = await generate_embedding(text)
        
        # pgvector's Vector column accepts a list directly
        # Create vector embedding record
        vector_embedding = VectorEmbedding(
            text=text[:10000],  # Limit text length to prevent issues
            embedding=embedding_vector,  # pgvector accepts list directly
            content_type=content_type,
            content_id=content_id,
            learner_id=learner_id,
            learning_plan_id=learning_plan_id,
            generated_content_id=generated_content_id,
            meta_data=json.dumps(meta_data) if meta_data else None
        )
        
        db.add(vector_embedding)
        db.commit()
        db.refresh(vector_embedding)
        
        return vector_embedding
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to create vector embedding: {str(e)}") from e


async def create_embeddings_for_content(
    db: Session,
    text: str,
    content_type: str,
    learner_id: Optional[int] = None,
    **kwargs
) -> Optional[VectorEmbedding]:
    """
    Helper function to create embeddings for various content types
    
    Args:
        db: Database session
        text: Text content to embed
        content_type: Type of content
        learner_id: Optional learner ID
        **kwargs: Additional foreign key parameters
        
    Returns:
        VectorEmbedding: Created embedding or None if failed
    """
    try:
        return await create_vector_embedding(
            db=db,
            text=text,
            content_type=content_type,
            learner_id=learner_id,
            **kwargs
        )
    except Exception as e:
        # Log error but don't fail the main operation
        print(f"Warning: Failed to create embedding for {content_type}: {str(e)}")
        return None

