from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict
from db.database import get_db
from db.models import Learner, GeneratedContent, User
from agents.content_generator import ContentGenerator, LessonContentOutput, QuizQuestion
from core.dependencies import get_current_user, verify_learner_access_helper
from core.vector_utils import create_embeddings_for_content
import json

router = APIRouter(prefix="/content", tags=["content"])
content_generator = ContentGenerator()


class GenerateContentRequest(BaseModel):
    learner_id: int
    module_name: str


class GenerateContentResponse(BaseModel):
    learner_id: int
    content_id: int
    module_name: str
    lesson_text: str
    quiz: List[Dict]
    message: str = "Content generated successfully"


@router.post("/generate", response_model=GenerateContentResponse, status_code=status.HTTP_201_CREATED)
async def generate_content(
    request: GenerateContentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate lesson content and quiz for a module (requires authentication)"""
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Call the agent
        result: LessonContentOutput = await content_generator.generate_content(
            module_name=request.module_name
        )
        
        # Convert quiz to dict for JSON storage
        quiz_dict = [
            {
                "question": q.question,
                "options": q.options,
                "answer": q.answer
            }
            for q in result.quiz
        ]
        
        # Save to database
        generated_content = GeneratedContent(
            learner_id=request.learner_id,
            module_name=request.module_name,
            lesson_text=result.lesson_text,
            quiz_json=quiz_dict
        )
        
        db.add(generated_content)
        db.commit()
        db.refresh(generated_content)
        
        # Create vector embeddings for the lesson text
        # This enables semantic search in the chatbot
        try:
            # Create embedding for the full lesson text
            await create_embeddings_for_content(
                db=db,
                text=result.lesson_text,
                content_type="lesson_text",
                learner_id=request.learner_id,
                generated_content_id=generated_content.id
            )
            
            # Also create embeddings for quiz questions (for better searchability)
            for quiz_item in result.quiz:
                quiz_text = f"{quiz_item.question} {' '.join(quiz_item.options)}"
                await create_embeddings_for_content(
                    db=db,
                    text=quiz_text,
                    content_type="quiz_question",
                    learner_id=request.learner_id,
                    generated_content_id=generated_content.id
                )
        except Exception as e:
            # Don't fail the request if embedding creation fails
            print(f"Warning: Failed to create embeddings for content: {str(e)}")
        
        return GenerateContentResponse(
            learner_id=request.learner_id,
            content_id=generated_content.id,
            module_name=request.module_name,
            lesson_text=result.lesson_text,
            quiz=quiz_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating content: {str(e)}"
        )

