"""
Mentor routes for viewing learner progress and managing assignments
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from pydantic import BaseModel
from db.database import get_db
from db.models import User, Learner, Progress, LearningPlan, learner_mentor_association
from core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/mentor", tags=["mentor"])


class LearnerProgressResponse(BaseModel):
    learner_id: int
    learner_name: str
    learner_email: str
    professional_role: str
    experience_years: int
    skill_map: dict
    progress: dict
    learning_plans: List[dict]
    
    class Config:
        from_attributes = True


class AssignMentorRequest(BaseModel):
    learner_id: int
    mentor_id: int


@router.get("/my-learners", response_model=List[LearnerProgressResponse])
async def get_my_learners(
    current_user: User = Depends(require_role(["mentor"])),
    db: Session = Depends(get_db)
):
    """Get all learners assigned to the current mentor"""
    if current_user.role != "mentor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can access this endpoint"
        )
    
    # Get learners assigned to this mentor using join
    learners = db.query(Learner).join(
        learner_mentor_association
    ).filter(
        and_(
            learner_mentor_association.c.mentor_id == current_user.id,
            learner_mentor_association.c.is_active == True
        )
    ).all()
    
    result = []
    for learner in learners:
        # Get progress
        progress = db.query(Progress).filter(
            Progress.learner_id == learner.id
        ).first()
        
        # Get learning plans
        learning_plans = db.query(LearningPlan).filter(
            LearningPlan.learner_id == learner.id
        ).all()
        
        result.append(LearnerProgressResponse(
            learner_id=learner.id,
            learner_name=learner.user.name,
            learner_email=learner.user.email,
            professional_role=learner.professional_role,
            experience_years=learner.experience_years,
            skill_map=learner.skill_map or {},
            progress={
                "completed_modules": progress.completed_modules if progress else [],
                "xp": progress.xp if progress else 0,
                "streak": progress.streak if progress else 0,
                "updated_at": progress.updated_at.isoformat() if progress and progress.updated_at else None
            } if progress else {
                "completed_modules": [],
                "xp": 0,
                "streak": 0,
                "updated_at": None
            },
            learning_plans=[plan.plan_json for plan in learning_plans]
        ))
    
    return result


@router.get("/learner/{learner_id}/progress", response_model=LearnerProgressResponse)
async def get_learner_progress(
    learner_id: int,
    current_user: User = Depends(require_role(["mentor"])),
    db: Session = Depends(get_db)
):
    """Get detailed progress of a specific learner"""
    # Verify mentor has access to this learner
    learner = db.query(Learner).join(
        learner_mentor_association
    ).filter(
        and_(
            Learner.id == learner_id,
            learner_mentor_association.c.mentor_id == current_user.id,
            learner_mentor_association.c.is_active == True
        )
    ).first()
    
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner not found or you don't have access to this learner"
        )
    
    # Get progress
    progress = db.query(Progress).filter(
        Progress.learner_id == learner.id
    ).first()
    
    # Get learning plans
    learning_plans = db.query(LearningPlan).filter(
        LearningPlan.learner_id == learner.id
    ).all()
    
    return LearnerProgressResponse(
        learner_id=learner.id,
        learner_name=learner.user.name,
        learner_email=learner.user.email,
        professional_role=learner.professional_role,
        experience_years=learner.experience_years,
        skill_map=learner.skill_map or {},
        progress={
            "completed_modules": progress.completed_modules if progress else [],
            "xp": progress.xp if progress else 0,
            "streak": progress.streak if progress else 0,
            "updated_at": progress.updated_at.isoformat() if progress and progress.updated_at else None
        } if progress else {
            "completed_modules": [],
            "xp": 0,
            "streak": 0,
            "updated_at": None
        },
        learning_plans=[plan.plan_json for plan in learning_plans]
    )

