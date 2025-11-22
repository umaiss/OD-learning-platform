from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List
from db.database import get_db
from db.models import Learner, LearningPlan
from agents.learning_path import LearningPathGenerator, LearningPathOutput, ModuleInfo
import json

router = APIRouter(prefix="/learning-path", tags=["learning-path"])
path_generator = LearningPathGenerator()


class GenerateLearningPathRequest(BaseModel):
    learner_id: int
    skill_map: Dict[str, str]
    experience: int
    role: str


class GenerateLearningPathResponse(BaseModel):
    learner_id: int
    learning_plan_id: int
    duration_weeks: int
    weekly_goals: List[str]
    milestones: List[str]
    modules: List[Dict]
    message: str = "Learning path generated successfully"


@router.post("/generate", response_model=GenerateLearningPathResponse, status_code=status.HTTP_201_CREATED)
async def generate_learning_path(
    request: GenerateLearningPathRequest,
    db: Session = Depends(get_db)
):
    """Generate a personalized learning path for a learner"""
    try:
        # Verify learner exists
        learner = db.query(Learner).filter(Learner.id == request.learner_id).first()
        if not learner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learner with id {request.learner_id} not found"
            )
        
        # Call the agent
        result: LearningPathOutput = await path_generator.generate_learning_path_plan(
            skill_map=request.skill_map,
            experience=request.experience,
            role=request.role
        )
        
        # Convert modules to dict for JSON storage
        modules_dict = [{"name": m.name, "description": m.description} for m in result.modules]
        
        # Create learning plan in database
        plan_json = {
            "duration_weeks": result.duration_weeks,
            "weekly_goals": result.weekly_goals,
            "milestones": result.milestones,
            "modules": modules_dict
        }
        
        learning_plan = LearningPlan(
            learner_id=request.learner_id,
            plan_json=plan_json
        )
        
        db.add(learning_plan)
        db.commit()
        db.refresh(learning_plan)
        
        return GenerateLearningPathResponse(
            learner_id=request.learner_id,
            learning_plan_id=learning_plan.id,
            duration_weeks=result.duration_weeks,
            weekly_goals=result.weekly_goals,
            milestones=result.milestones,
            modules=modules_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating learning path: {str(e)}"
        )

