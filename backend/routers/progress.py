from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from db.database import get_db
from db.models import Learner, Progress, User
from core.dependencies import get_current_user, verify_learner_access_helper

router = APIRouter(prefix="/progress", tags=["progress"])


class UpdateProgressRequest(BaseModel):
    learner_id: int
    completed_modules: Optional[List[str]] = None
    xp: Optional[int] = None
    streak: Optional[int] = None


class UpdateProgressResponse(BaseModel):
    learner_id: int
    progress_id: int
    completed_modules: List[str]
    xp: int
    streak: int
    message: str = "Progress updated successfully"


@router.post("/update", response_model=UpdateProgressResponse, status_code=status.HTTP_200_OK)
async def update_progress(
    request: UpdateProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update learner progress (requires authentication)"""
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Get or create progress record
        progress = db.query(Progress).filter(
            Progress.learner_id == request.learner_id
        ).first()
        
        if progress:
            # Update existing progress
            if request.completed_modules is not None:
                current_modules = progress.completed_modules or []
                # Merge with existing, avoiding duplicates
                updated_modules = list(set(current_modules + request.completed_modules))
                progress.completed_modules = updated_modules
            
            if request.xp is not None:
                progress.xp = request.xp
            
            if request.streak is not None:
                progress.streak = request.streak
            
            db.commit()
            db.refresh(progress)
        else:
            # Create new progress record
            progress = Progress(
                learner_id=request.learner_id,
                completed_modules=request.completed_modules or [],
                xp=request.xp or 0,
                streak=request.streak or 0
            )
            db.add(progress)
            db.commit()
            db.refresh(progress)
        
        return UpdateProgressResponse(
            learner_id=request.learner_id,
            progress_id=progress.id,
            completed_modules=progress.completed_modules or [],
            xp=progress.xp,
            streak=progress.streak
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating progress: {str(e)}"
        )

