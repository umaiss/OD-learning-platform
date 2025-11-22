from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict
from db.database import get_db
from db.models import Learner
from agents.skill_profiler import SkillProfiler, SkillProfileOutput

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
    db: Session = Depends(get_db)
):
    """Generate skill profile for a learner"""
    try:
        # Call the agent
        result: SkillProfileOutput = await skill_profiler.generate_skill_profile(
            self_assessment=request.self_assessment,
            role=request.role,
            experience=request.experience
        )
        
        # Get or create learner
        learner = db.query(Learner).filter(Learner.id == request.learner_id).first()
        if not learner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learner with id {request.learner_id} not found"
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

