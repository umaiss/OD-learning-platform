from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict
from db.database import get_db
from db.models import Learner
from db.models import User
from agents.skill_profiler import SkillProfiler, SkillProfileOutput
from core.dependencies import get_current_user, verify_learner_access_helper

router = APIRouter(prefix="/profile", tags=["profile"])
skill_profiler = SkillProfiler()


class GenerateProfileRequest(BaseModel):
    learner_id: int
    self_assessment: str
    role: str
    experience: int


class GenerateProfileResponse(BaseModel):
    learner_id: int
    strengths: list
    gaps: list
    skill_map: Dict[str, str]
    message: str = "Profile generated successfully"


@router.post("/generate", response_model=GenerateProfileResponse, status_code=status.HTTP_201_CREATED)
async def generate_profile(
    request: GenerateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate skill profile for a learner (requires authentication)"""
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Call the agent
        result: SkillProfileOutput = await skill_profiler.generate_skill_profile(
            self_assessment=request.self_assessment,
            role=request.role,
            experience=request.experience
        )
        
        # Update learner with profile data
        learner.skill_map = result.skill_map
        learner.strengths = "\n".join(result.strengths)
        learner.gaps = "\n".join(result.gaps)
        
        db.commit()
        db.refresh(learner)
        
        return GenerateProfileResponse(
            learner_id=learner.id,
            strengths=result.strengths,
            gaps=result.gaps,
            skill_map=result.skill_map
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating profile: {str(e)}"
        )

