from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from db.database import get_db
from db.models import Progress

router = APIRouter(prefix="/progress", tags=["progress"])


class ProgressCreate(BaseModel):
    user_id: int
    entity_type: str  # learning_path, mission, module
    entity_id: int
    completion_percentage: float = 0.0
    time_spent: int = 0  # in minutes
    meta_data: Optional[dict] = None


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    entity_type: str
    entity_id: int
    completion_percentage: float
    time_spent: int
    metadata: Optional[dict]
    
    class Config:
        from_attributes = True


class ProgressUpdate(BaseModel):
    completion_percentage: Optional[float] = None
    time_spent: Optional[int] = None
    meta_data: Optional[dict] = None


@router.post("/", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
async def create_progress(
    progress: ProgressCreate,
    db: Session = Depends(get_db)
):
    """Create a new progress record"""
    db_progress = Progress(**progress.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress


@router.get("/user/{user_id}", response_model=List[ProgressResponse])
async def get_user_progress(
    user_id: int,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all progress records for a user"""
    query = db.query(Progress).filter(Progress.user_id == user_id)
    
    if entity_type:
        query = query.filter(Progress.entity_type == entity_type)
    
    progress_records = query.all()
    return progress_records


@router.get("/user/{user_id}/entity/{entity_type}/{entity_id}", response_model=ProgressResponse)
async def get_entity_progress(
    user_id: int,
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db)
):
    """Get progress for a specific entity"""
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.entity_type == entity_type,
        Progress.entity_id == entity_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress record not found"
        )
    
    return progress


@router.put("/{progress_id}", response_model=ProgressResponse)
async def update_progress(
    progress_id: int,
    progress_update: ProgressUpdate,
    db: Session = Depends(get_db)
):
    """Update a progress record"""
    db_progress = db.query(Progress).filter(Progress.id == progress_id).first()
    if not db_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress record not found"
        )
    
    update_data = progress_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_progress, key, value)
    
    db.commit()
    db.refresh(db_progress)
    return db_progress


@router.patch("/user/{user_id}/entity/{entity_type}/{entity_id}", response_model=ProgressResponse)
async def upsert_progress(
    user_id: int,
    entity_type: str,
    entity_id: int,
    progress_update: ProgressUpdate,
    db: Session = Depends(get_db)
):
    """Create or update progress for a specific entity"""
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.entity_type == entity_type,
        Progress.entity_id == entity_id
    ).first()
    
    if progress:
        # Update existing
        update_data = progress_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(progress, key, value)
    else:
        # Create new
        progress_data = {
            "user_id": user_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            **progress_update.dict(exclude_unset=True)
        }
        progress = Progress(**progress_data)
        db.add(progress)
    
    db.commit()
    db.refresh(progress)
    return progress


@router.get("/user/{user_id}/stats", response_model=dict)
async def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get aggregated progress statistics for a user"""
    progress_records = db.query(Progress).filter(Progress.user_id == user_id).all()
    
    total_time = sum(p.time_spent for p in progress_records)
    avg_completion = sum(p.completion_percentage for p in progress_records) / len(progress_records) if progress_records else 0
    
    stats_by_type = {}
    for record in progress_records:
        if record.entity_type not in stats_by_type:
            stats_by_type[record.entity_type] = {
                "count": 0,
                "total_completion": 0,
                "total_time": 0
            }
        stats_by_type[record.entity_type]["count"] += 1
        stats_by_type[record.entity_type]["total_completion"] += record.completion_percentage
        stats_by_type[record.entity_type]["total_time"] += record.time_spent
    
    return {
        "total_records": len(progress_records),
        "total_time_spent_minutes": total_time,
        "average_completion": round(avg_completion, 2),
        "by_entity_type": {
            k: {
                "count": v["count"],
                "average_completion": round(v["total_completion"] / v["count"], 2) if v["count"] > 0 else 0,
                "total_time_minutes": v["total_time"]
            }
            for k, v in stats_by_type.items()
        }
    }


@router.delete("/{progress_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_progress(
    progress_id: int,
    db: Session = Depends(get_db)
):
    """Delete a progress record"""
    db_progress = db.query(Progress).filter(Progress.id == progress_id).first()
    if not db_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress record not found"
        )
    
    db.delete(db_progress)
    db.commit()
    return None

