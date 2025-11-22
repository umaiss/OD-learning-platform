from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from db.database import get_db
from db.models import SkillProfile
from agents.skill_profiler import SkillProfiler

router = APIRouter(prefix="/skill-profile", tags=["skill-profile"])
skill_profiler = SkillProfiler()


class SkillProfileCreate(BaseModel):
    user_id: int
    skill_name: str
    skill_level: str
    description: Optional[str] = None
    meta_data: Optional[dict] = None


class SkillProfileResponse(BaseModel):
    id: int
    user_id: int
    skill_name: str
    skill_level: str
    description: Optional[str]
    metadata: Optional[dict]
    
    class Config:
        from_attributes = True


class SkillAssessmentRequest(BaseModel):
    user_input: str
    context: Optional[dict] = None


@router.post("/assess", response_model=dict)
async def assess_skills(request: SkillAssessmentRequest):
    """Assess user skills from input text"""
    try:
        result = await skill_profiler.profile_skills(
            user_input=request.user_input,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assessing skills: {str(e)}"
        )


@router.post("/", response_model=SkillProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_skill_profile(
    profile: SkillProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new skill profile"""
    db_profile = SkillProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.get("/user/{user_id}", response_model=List[SkillProfileResponse])
async def get_user_skill_profiles(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all skill profiles for a user"""
    profiles = db.query(SkillProfile).filter(SkillProfile.user_id == user_id).all()
    return profiles


@router.get("/{profile_id}", response_model=SkillProfileResponse)
async def get_skill_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific skill profile"""
    profile = db.query(SkillProfile).filter(SkillProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill profile not found"
        )
    return profile


@router.put("/{profile_id}", response_model=SkillProfileResponse)
async def update_skill_profile(
    profile_id: int,
    profile: SkillProfileCreate,
    db: Session = Depends(get_db)
):
    """Update a skill profile"""
    db_profile = db.query(SkillProfile).filter(SkillProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill profile not found"
        )
    
    for key, value in profile.dict().items():
        setattr(db_profile, key, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """Delete a skill profile"""
    db_profile = db.query(SkillProfile).filter(SkillProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill profile not found"
        )
    
    db.delete(db_profile)
    db.commit()
    return None

