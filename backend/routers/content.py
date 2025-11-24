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


class GenerateWeekQuizRequest(BaseModel):
    learner_id: int
    learning_plan_id: int
    week_number: int


class GenerateWeekQuizResponse(BaseModel):
    learner_id: int
    learning_plan_id: int
    week_number: int
    quiz: List[Dict]
    message: str = "Week quiz generated successfully"


@router.post("/generate-week-quiz", response_model=GenerateWeekQuizResponse, status_code=status.HTTP_201_CREATED)
async def generate_week_quiz(
    request: GenerateWeekQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a quiz for a specific week based on all modules in that week (requires authentication)"""
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Get learning plan
        from db.models import LearningPlan
        learning_plan = db.query(LearningPlan).filter(
            LearningPlan.id == request.learning_plan_id,
            LearningPlan.learner_id == request.learner_id
        ).first()
        
        if not learning_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learning plan not found"
            )
        
        # Find the week in the plan
        plan_json = learning_plan.plan_json
        weekly_goals = plan_json.get("weekly_goals", [])
        week_data = None
        for weekly_goal in weekly_goals:
            if weekly_goal.get("week") == request.week_number:
                week_data = weekly_goal
                break
        
        if not week_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Week {request.week_number} not found in learning plan"
            )
        
        # Build topic string from week goals and modules
        modules = week_data.get("modules", [])
        module_names = [m.get("name", "") for m in modules]
        goals = week_data.get("goals", [])
        
        # Create a comprehensive topic description
        topic = f"Week {request.week_number}: {'; '.join(goals)}. Modules: {', '.join(module_names)}"
        
        # Generate quiz by combining all modules in the week
        # Create a comprehensive quiz based on all week content
        if not modules:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No modules found in this week"
            )
        
        # Generate quiz questions based on all modules in the week
        # We'll use the content generator to create a comprehensive quiz
        from core.llm_ollama import generate_structured
        from agents.content_generator import QuizQuestion
        
        class WeekQuizOutput(BaseModel):
            quiz: List[QuizQuestion]
        
        quiz_prompt = f"""Create a comprehensive quiz for Week {request.week_number} covering the following topics:

Week Goals: {', '.join(goals)}
Modules: {', '.join(module_names)}

Generate 10 multiple-choice questions that test understanding of all the concepts covered in this week.
Each question should have 4 options with one correct answer.
Make sure questions cover different aspects of the week's content."""
        
        try:
            quiz_result = await generate_structured(
                prompt=quiz_prompt,
                schema=WeekQuizOutput
            )
            
            quiz_dict = [
                {
                    "question": q.question,
                    "options": q.options,
                    "answer": q.answer
                }
                for q in quiz_result.quiz
            ]
        except Exception as e:
            # Fallback: generate content for the first module and use its quiz
            first_module = modules[0]
            result: LessonContentOutput = await content_generator.generate_content(
                module_name=first_module.get("name", "")
            )
            quiz_dict = [
                {
                    "question": q.question,
                    "options": q.options,
                    "answer": q.answer
                }
                for q in result.quiz
            ]
        
        return GenerateWeekQuizResponse(
            learner_id=request.learner_id,
            learning_plan_id=request.learning_plan_id,
            week_number=request.week_number,
            quiz=quiz_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating week quiz: {str(e)}"
        )

