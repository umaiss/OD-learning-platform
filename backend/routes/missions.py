from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from db.database import get_db
from db.models import Mission
from agents.missions import MissionGenerator

router = APIRouter(prefix="/missions", tags=["missions"])
mission_generator = MissionGenerator()


class MissionCreate(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    mission_type: str
    difficulty: str
    points: int = 0
    meta_data: Optional[dict] = None


class MissionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    mission_type: str
    difficulty: str
    status: str
    points: int
    metadata: Optional[dict]
    
    class Config:
        from_attributes = True


class GenerateMissionRequest(BaseModel):
    skill: str
    mission_type: str = "practice"
    difficulty: str = "intermediate"
    user_level: Optional[str] = None


class MissionEvaluationRequest(BaseModel):
    mission_id: int
    user_submission: str


@router.post("/generate", response_model=dict)
async def generate_mission(request: GenerateMissionRequest):
    """Generate a learning mission"""
    try:
        result = await mission_generator.generate_mission(
            skill=request.skill,
            mission_type=request.mission_type,
            difficulty=request.difficulty,
            user_level=request.user_level
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating mission: {str(e)}"
        )


@router.post("/evaluate", response_model=dict)
async def evaluate_mission(request: MissionEvaluationRequest, db: Session = Depends(get_db)):
    """Evaluate mission completion"""
    try:
        mission = db.query(Mission).filter(Mission.id == request.mission_id).first()
        if not mission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mission not found"
            )
        
        mission_dict = {
            "title": mission.title,
            "description": mission.description,
            "mission_type": mission.mission_type,
            "difficulty": mission.difficulty
        }
        
        result = await mission_generator.evaluate_mission_completion(
            mission=mission_dict,
            user_submission=request.user_submission
        )
        
        # Update mission status if completed
        if result.get("completed"):
            mission.status = "completed"
            db.commit()
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating mission: {str(e)}"
        )


@router.post("/", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
async def create_mission(
    mission: MissionCreate,
    db: Session = Depends(get_db)
):
    """Create a new mission"""
    db_mission = Mission(**mission.dict())
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    return db_mission


@router.get("/user/{user_id}", response_model=List[MissionResponse])
async def get_user_missions(
    user_id: int,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all missions for a user"""
    query = db.query(Mission).filter(Mission.user_id == user_id)
    
    if status_filter:
        query = query.filter(Mission.status == status_filter)
    
    missions = query.all()
    return missions


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(
    mission_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific mission"""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )
    return mission


@router.put("/{mission_id}", response_model=MissionResponse)
async def update_mission(
    mission_id: int,
    mission: MissionCreate,
    db: Session = Depends(get_db)
):
    """Update a mission"""
    db_mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not db_mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )
    
    for key, value in mission.dict().items():
        setattr(db_mission, key, value)
    
    db.commit()
    db.refresh(db_mission)
    return db_mission


@router.patch("/{mission_id}/complete", response_model=MissionResponse)
async def complete_mission(
    mission_id: int,
    db: Session = Depends(get_db)
):
    """Mark a mission as completed"""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )
    
    mission.status = "completed"
    from datetime import datetime
    mission.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(mission)
    return mission


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mission(
    mission_id: int,
    db: Session = Depends(get_db)
):
    """Delete a mission"""
    db_mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not db_mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )
    
    db.delete(db_mission)
    db.commit()
    return None

