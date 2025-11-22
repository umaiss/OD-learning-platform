from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Optional
from db.database import get_db
from db.models import Learner
from db.models import User
from agents.skill_profiler import SkillProfiler, SkillProfileOutput, LinkedInProfile, EndorsedSkill as AgentEndorsedSkill
from core.dependencies import get_current_user, verify_learner_access_helper
from core.vector_utils import create_embeddings_for_content

router = APIRouter(prefix="/profile", tags=["profile"])
skill_profiler = SkillProfiler()


class EndorsedSkill(BaseModel):
    """LinkedIn endorsed skill"""
    skill: str
    endorsements: int


class LinkedInProfileInput(BaseModel):
    """LinkedIn profile input data"""
    id: Optional[int] = None
    learnerId: Optional[int] = None
    username: Optional[str] = None
    fullName: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    endorsedSkills: Optional[List[EndorsedSkill]] = None
    connections: Optional[int] = None
    followers: Optional[int] = None


class GenerateProfileRequest(BaseModel):
    learner_id: int
    current_role: str
    primary_stack: List[str]  # Array of technologies like ["JavaScript", "Python", "React"]
    learning_goals: str
    skill_rate: Optional[Dict[str, str]] = None  # Optional: {"JavaScript": "8/10", "Python": "7/10"}
    linkedin_profile: Optional[LinkedInProfileInput] = None


class GenerateProfileResponse(BaseModel):
    learner_id: int
    ai_analysis: str  # AI analysis and remarks
    strengths: List[str]
    growth_areas: List[str]  # Renamed from gaps
    skill_map: Dict[str, str]
    message: str = "Profile generated successfully. Use /api/v1/profile/save to store it."


class SaveProfileRequest(BaseModel):
    learner_id: int
    learning_goals: str  # User's learning goals and career objectives
    ai_analysis: str
    strengths: List[str]
    growth_areas: List[str]
    skill_map: Dict[str, str]


class SaveProfileResponse(BaseModel):
    learner_id: int
    message: str = "Profile saved successfully"


@router.post("/generate", response_model=GenerateProfileResponse, status_code=status.HTTP_201_CREATED)
async def generate_profile(
    request: GenerateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate comprehensive skill profile for a learner (requires authentication)"""
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Convert LinkedIn profile input to LinkedInProfile model if provided
        linkedin_profile = None
        if request.linkedin_profile:
            # Convert EndorsedSkill from request to agent's EndorsedSkill model
            endorsed_skills_list = None
            if request.linkedin_profile.endorsedSkills:
                endorsed_skills_list = [
                    AgentEndorsedSkill(skill=skill.skill, endorsements=skill.endorsements)
                    for skill in request.linkedin_profile.endorsedSkills
                ]
            
            linkedin_profile = LinkedInProfile(
                id=request.linkedin_profile.id,
                learnerId=request.linkedin_profile.learnerId,
                username=request.linkedin_profile.username,
                fullName=request.linkedin_profile.fullName,
                headline=request.linkedin_profile.headline,
                location=request.linkedin_profile.location,
                endorsedSkills=endorsed_skills_list,
                connections=request.linkedin_profile.connections,
                followers=request.linkedin_profile.followers
            )
        
        # Call the agent with new parameters
        result: SkillProfileOutput = await skill_profiler.generate_skill_profile(
            current_role=request.current_role,
            primary_stack=request.primary_stack,
            learning_goals=request.learning_goals,
            skill_rate=request.skill_rate,
            linkedin_profile=linkedin_profile
        )
        
        # Note: Profile is generated but not automatically saved
        # Use /api/v1/profile/save endpoint to save the generated profile
        
        return GenerateProfileResponse(
            learner_id=learner.id,
            ai_analysis=result.ai_analysis,
            strengths=result.strengths,
            growth_areas=result.growth_areas,
            skill_map=result.skill_map
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating profile: {str(e)}"
        )


@router.post("/save", response_model=SaveProfileResponse, status_code=status.HTTP_200_OK)
async def save_profile(
    request: SaveProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save/update the generated profile for a learner (requires authentication)"""
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Verify learner_id matches
        if learner.id != request.learner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="learner_id in request does not match authenticated learner"
            )
        
        # Update learner with profile data
        learner.learning_goals = request.learning_goals
        learner.skill_map = request.skill_map
        learner.strengths = "\n".join(request.strengths)
        learner.gaps = "\n".join(request.growth_areas)
        learner.ai_analysis = request.ai_analysis
        
        db.commit()
        db.refresh(learner)
        
        # Create vector embeddings for the skill profile
        # This enables semantic search in the chatbot
        try:
            # Create a text representation of the skill profile for embedding
            profile_text_parts = [
                f"Learning Goals: {request.learning_goals}",
                f"AI Analysis: {request.ai_analysis}",
                f"Strengths: {', '.join(request.strengths)}",
                f"Growth Areas: {', '.join(request.growth_areas)}",
                "Skill Map:"
            ]
            
            for skill, level in request.skill_map.items():
                profile_text_parts.append(f"  {skill}: {level}")
            
            profile_text = "\n".join(profile_text_parts)
            
            await create_embeddings_for_content(
                db=db,
                text=profile_text,
                content_type="skill_profile",
                learner_id=request.learner_id
            )
        except Exception as e:
            # Don't fail the request if embedding creation fails
            print(f"Warning: Failed to create embeddings for skill profile: {str(e)}")
        
        return SaveProfileResponse(
            learner_id=learner.id,
            message="Profile saved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving profile: {str(e)}"
        )

