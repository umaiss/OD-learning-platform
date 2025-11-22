from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from db.database import get_db
from db.models import LearningPath, Module
from agents.learning_path import LearningPathGenerator

router = APIRouter(prefix="/learning-path", tags=["learning-path"])
path_generator = LearningPathGenerator()


class LearningPathCreate(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    skill_goal: str
    difficulty: str
    estimated_duration: Optional[int] = None
    meta_data: Optional[dict] = None


class LearningPathResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    skill_goal: str
    difficulty: str
    estimated_duration: Optional[int]
    status: str
    metadata: Optional[dict]
    
    class Config:
        from_attributes = True


class GeneratePathRequest(BaseModel):
    skill_goal: str
    current_skills: dict
    difficulty: str = "intermediate"
    duration_hours: Optional[int] = None


@router.post("/generate", response_model=dict)
async def generate_learning_path(request: GeneratePathRequest):
    """Generate a personalized learning path"""
    try:
        result = await path_generator.generate_learning_path(
            skill_goal=request.skill_goal,
            current_skills=request.current_skills,
            difficulty=request.difficulty,
            duration_hours=request.duration_hours
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating learning path: {str(e)}"
        )


@router.post("/", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
async def create_learning_path(
    path: LearningPathCreate,
    db: Session = Depends(get_db)
):
    """Create a new learning path"""
    db_path = LearningPath(**path.dict())
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    return db_path


@router.get("/user/{user_id}", response_model=List[LearningPathResponse])
async def get_user_learning_paths(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all learning paths for a user"""
    paths = db.query(LearningPath).filter(LearningPath.user_id == user_id).all()
    return paths


@router.get("/{path_id}", response_model=LearningPathResponse)
async def get_learning_path(
    path_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific learning path"""
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )
    return path


@router.put("/{path_id}", response_model=LearningPathResponse)
async def update_learning_path(
    path_id: int,
    path: LearningPathCreate,
    db: Session = Depends(get_db)
):
    """Update a learning path"""
    db_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not db_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )
    
    for key, value in path.dict().items():
        setattr(db_path, key, value)
    
    db.commit()
    db.refresh(db_path)
    return db_path


@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_learning_path(
    path_id: int,
    db: Session = Depends(get_db)
):
    """Delete a learning path"""
    db_path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not db_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found"
        )
    
    db.delete(db_path)
    db.commit()
    return None

