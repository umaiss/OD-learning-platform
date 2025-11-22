"""
API endpoints for module progress tracking and learning materials
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
from db.database import get_db
from db.models import Learner, LearningPlan, ModuleProgress, WeekProgress, User, Progress
from core.dependencies import get_current_user, verify_learner_access_helper

router = APIRouter(prefix="/module-progress", tags=["module-progress"])


class LearningMaterial(BaseModel):
    """Learning material structure"""
    title: str
    url: str  # URL to Udemy, Coursera, etc.
    platform: str  # "udemy", "coursera", "youtube", "other"
    type: Optional[str] = "course"  # "course", "video", "article", "tutorial"
    estimated_hours: Optional[int] = None
    description: Optional[str] = None


class AddLearningMaterialRequest(BaseModel):
    """Request to add learning materials to a module"""
    learner_id: int
    learning_plan_id: int
    week_number: int
    module_name: str
    learning_materials: List[LearningMaterial]


class AddLearningMaterialResponse(BaseModel):
    """Response after adding learning materials"""
    learner_id: int
    learning_plan_id: int
    week_number: int
    module_name: str
    learning_materials: List[LearningMaterial]
    message: str = "Learning materials added successfully"


class UpdateModuleProgressRequest(BaseModel):
    """Request to update module progress"""
    learner_id: int
    learning_plan_id: int
    week_number: int
    module_name: str
    completion_percentage: float  # 0.0 to 100.0
    time_spent_minutes: Optional[int] = 0
    mark_completed: Optional[bool] = False  # If True, marks as completed regardless of percentage


class ModuleProgressResponse(BaseModel):
    """Module progress response"""
    id: int
    learner_id: int
    learning_plan_id: int
    week_number: int
    module_name: str
    completion_percentage: float
    is_completed: bool
    completed_at: Optional[datetime]
    time_spent_minutes: int
    updated_at: datetime


class UpdateModuleProgressResponse(BaseModel):
    """Response after updating module progress"""
    module_progress: ModuleProgressResponse
    week_completed: bool  # Whether the week was marked as completed
    message: str = "Module progress updated successfully"


class GetProgressRequest(BaseModel):
    """Request to get progress for a learning plan"""
    learner_id: int
    learning_plan_id: int


class WeekProgressResponse(BaseModel):
    """Week progress response"""
    week_number: int
    is_completed: bool
    completed_at: Optional[datetime]
    completed_modules_count: int
    total_modules_count: int
    xp_earned: int
    modules: List[ModuleProgressResponse]


class LearningPlanProgressResponse(BaseModel):
    """Complete learning plan progress response"""
    learner_id: int
    learning_plan_id: int
    total_weeks: int
    completed_weeks: int
    total_modules: int
    completed_modules: int
    total_xp: int
    earned_xp: int
    weeks: List[WeekProgressResponse]


@router.post("/add-materials", response_model=AddLearningMaterialResponse, status_code=status.HTTP_200_OK)
async def add_learning_materials(
    request: AddLearningMaterialRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add learning materials (Udemy, Coursera, etc.) to a module (requires authentication)"""
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Verify learning plan exists and belongs to learner
        learning_plan = db.query(LearningPlan).filter(
            LearningPlan.id == request.learning_plan_id,
            LearningPlan.learner_id == request.learner_id
        ).first()
        
        if not learning_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learning plan not found"
            )
        
        # Get the plan JSON
        plan_json = learning_plan.plan_json
        
        # Find the week and module in the plan
        weekly_goals = plan_json.get("weekly_goals", [])
        week_found = False
        module_found = False
        
        for weekly_goal in weekly_goals:
            if weekly_goal.get("week") == request.week_number:
                week_found = True
                modules = weekly_goal.get("modules", [])
                
                for module in modules:
                    if module.get("name") == request.module_name:
                        module_found = True
                        # Add learning materials to the module
                        if "learning_materials" not in module:
                            module["learning_materials"] = []
                        
                        # Convert Pydantic models to dicts
                        materials_dict = [mat.dict() for mat in request.learning_materials]
                        module["learning_materials"] = materials_dict
                        break
                
                if module_found:
                    break
        
        if not week_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Week {request.week_number} not found in learning plan"
            )
        
        if not module_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{request.module_name}' not found in week {request.week_number}"
            )
        
        # Update the plan JSON
        learning_plan.plan_json = plan_json
        db.commit()
        db.refresh(learning_plan)
        
        return AddLearningMaterialResponse(
            learner_id=request.learner_id,
            learning_plan_id=request.learning_plan_id,
            week_number=request.week_number,
            module_name=request.module_name,
            learning_materials=request.learning_materials
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding learning materials: {str(e)}"
        )


@router.post("/update", response_model=UpdateModuleProgressResponse, status_code=status.HTTP_200_OK)
async def update_module_progress(
    request: UpdateModuleProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update module progress and auto-mark week as completed if all modules are done (requires authentication)"""
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Verify learning plan exists
        learning_plan = db.query(LearningPlan).filter(
            LearningPlan.id == request.learning_plan_id,
            LearningPlan.learner_id == request.learner_id
        ).first()
        
        if not learning_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learning plan not found"
            )
        
        # Validate completion percentage
        if request.completion_percentage < 0 or request.completion_percentage > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="completion_percentage must be between 0 and 100"
            )
        
        # Get or create module progress
        module_progress = db.query(ModuleProgress).filter(
            ModuleProgress.learner_id == request.learner_id,
            ModuleProgress.learning_plan_id == request.learning_plan_id,
            ModuleProgress.week_number == request.week_number,
            ModuleProgress.module_name == request.module_name
        ).first()
        
        if module_progress:
            # Update existing progress
            module_progress.completion_percentage = request.completion_percentage
            module_progress.time_spent_minutes = request.time_spent_minutes or module_progress.time_spent_minutes
            
            # Mark as completed if requested or if percentage is 100
            if request.mark_completed or request.completion_percentage >= 100.0:
                module_progress.is_completed = True
                if not module_progress.completed_at:
                    module_progress.completed_at = datetime.now(timezone.utc)
            else:
                module_progress.is_completed = False
                module_progress.completed_at = None
        else:
            # Create new progress record
            is_completed = request.mark_completed or request.completion_percentage >= 100.0
            module_progress = ModuleProgress(
                learner_id=request.learner_id,
                learning_plan_id=request.learning_plan_id,
                week_number=request.week_number,
                module_name=request.module_name,
                completion_percentage=request.completion_percentage,
                time_spent_minutes=request.time_spent_minutes or 0,
                is_completed=is_completed,
                completed_at=datetime.now(timezone.utc) if is_completed else None
            )
            db.add(module_progress)
        
        db.commit()
        db.refresh(module_progress)
        
        # Check if all modules in the week are completed
        week_completed = await _check_and_mark_week_completed(
            db=db,
            learner_id=request.learner_id,
            learning_plan_id=request.learning_plan_id,
            week_number=request.week_number,
            learning_plan=learning_plan
        )
        
        # Update learner's overall progress
        await _update_learner_progress(
            db=db,
            learner_id=request.learner_id,
            learning_plan_id=request.learning_plan_id
        )
        
        return UpdateModuleProgressResponse(
            module_progress=ModuleProgressResponse(
                id=module_progress.id,
                learner_id=module_progress.learner_id,
                learning_plan_id=module_progress.learning_plan_id,
                week_number=module_progress.week_number,
                module_name=module_progress.module_name,
                completion_percentage=module_progress.completion_percentage,
                is_completed=module_progress.is_completed,
                completed_at=module_progress.completed_at,
                time_spent_minutes=module_progress.time_spent_minutes,
                updated_at=module_progress.updated_at
            ),
            week_completed=week_completed
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating module progress: {str(e)}"
        )


@router.post("/get-progress", response_model=LearningPlanProgressResponse, status_code=status.HTTP_200_OK)
async def get_progress(
    request: GetProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete progress for a learning plan (requires authentication)"""
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Get learning plan
        learning_plan = db.query(LearningPlan).filter(
            LearningPlan.id == request.learning_plan_id,
            LearningPlan.learner_id == request.learner_id
        ).first()
        
        if not learning_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learning plan not found"
            )
        
        plan_json = learning_plan.plan_json
        weekly_goals = plan_json.get("weekly_goals", [])
        total_weeks = len(weekly_goals)
        
        # Get all week progress records
        week_progress_records = db.query(WeekProgress).filter(
            WeekProgress.learner_id == request.learner_id,
            WeekProgress.learning_plan_id == request.learning_plan_id
        ).all()
        
        week_progress_map = {wp.week_number: wp for wp in week_progress_records}
        
        # Get all module progress records
        module_progress_records = db.query(ModuleProgress).filter(
            ModuleProgress.learner_id == request.learner_id,
            ModuleProgress.learning_plan_id == request.learning_plan_id
        ).all()
        
        # Organize module progress by week
        module_progress_by_week = {}
        for mp in module_progress_records:
            if mp.week_number not in module_progress_by_week:
                module_progress_by_week[mp.week_number] = []
            module_progress_by_week[mp.week_number].append(mp)
        
        # Build response
        weeks_response = []
        total_modules = 0
        completed_modules = 0
        completed_weeks = 0
        total_xp = plan_json.get("total_xp", 0)
        earned_xp = 0
        
        for weekly_goal in weekly_goals:
            week_num = weekly_goal.get("week")
            modules = weekly_goal.get("modules", [])
            total_modules += len(modules)
            
            # Get week progress
            week_progress = week_progress_map.get(week_num)
            
            # Get module progress for this week
            module_progress_list = module_progress_by_week.get(week_num, [])
            completed_modules_count = sum(1 for mp in module_progress_list if mp.is_completed)
            
            # Count completed modules from progress records
            for module in modules:
                module_name = module.get("name")
                module_prog = next(
                    (mp for mp in module_progress_list if mp.module_name == module_name),
                    None
                )
                if module_prog and module_prog.is_completed:
                    completed_modules += 1
            
            week_xp = 0
            if week_progress and week_progress.is_completed:
                week_xp = weekly_goal.get("xp", 0)
                earned_xp += week_xp
                completed_weeks += 1
            
            weeks_response.append(WeekProgressResponse(
                week_number=week_num,
                is_completed=week_progress.is_completed if week_progress else False,
                completed_at=week_progress.completed_at if week_progress else None,
                completed_modules_count=completed_modules_count,
                total_modules_count=len(modules),
                xp_earned=week_xp,
                modules=[
                    ModuleProgressResponse(
                        id=mp.id,
                        learner_id=mp.learner_id,
                        learning_plan_id=mp.learning_plan_id,
                        week_number=mp.week_number,
                        module_name=mp.module_name,
                        completion_percentage=mp.completion_percentage,
                        is_completed=mp.is_completed,
                        completed_at=mp.completed_at,
                        time_spent_minutes=mp.time_spent_minutes,
                        updated_at=mp.updated_at
                    )
                    for mp in module_progress_list
                ]
            ))
        
        return LearningPlanProgressResponse(
            learner_id=request.learner_id,
            learning_plan_id=request.learning_plan_id,
            total_weeks=total_weeks,
            completed_weeks=completed_weeks,
            total_modules=total_modules,
            completed_modules=completed_modules,
            total_xp=total_xp,
            earned_xp=earned_xp,
            weeks=weeks_response
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting progress: {str(e)}"
        )


async def _check_and_mark_week_completed(
    db: Session,
    learner_id: int,
    learning_plan_id: int,
    week_number: int,
    learning_plan: LearningPlan
) -> bool:
    """Check if all modules in a week are completed and mark week as completed if so"""
    # Get the plan structure
    plan_json = learning_plan.plan_json
    weekly_goals = plan_json.get("weekly_goals", [])
    
    # Find the week
    week_data = None
    for weekly_goal in weekly_goals:
        if weekly_goal.get("week") == week_number:
            week_data = weekly_goal
            break
    
    if not week_data:
        return False
    
    modules = week_data.get("modules", [])
    total_modules = len(modules)
    
    if total_modules == 0:
        return False
    
    # Get all module progress for this week
    module_progress_list = db.query(ModuleProgress).filter(
        ModuleProgress.learner_id == learner_id,
        ModuleProgress.learning_plan_id == learning_plan_id,
        ModuleProgress.week_number == week_number
    ).all()
    
    # Check if all modules are completed
    completed_count = sum(1 for mp in module_progress_list if mp.is_completed)
    
    # Get week progress record
    week_progress = db.query(WeekProgress).filter(
        WeekProgress.learner_id == learner_id,
        WeekProgress.learning_plan_id == learning_plan_id,
        WeekProgress.week_number == week_number
    ).first()
    
    if completed_count == total_modules:
        # All modules completed - mark week as completed
        if week_progress:
            if not week_progress.is_completed:
                week_progress.is_completed = True
                week_progress.completed_at = datetime.now(timezone.utc)
                week_progress.completed_modules_count = completed_count
                week_progress.total_modules_count = total_modules
                week_progress.xp_earned = week_data.get("xp", 0)
        else:
            week_progress = WeekProgress(
                learner_id=learner_id,
                learning_plan_id=learning_plan_id,
                week_number=week_number,
                is_completed=True,
                completed_at=datetime.now(timezone.utc),
                completed_modules_count=completed_count,
                total_modules_count=total_modules,
                xp_earned=week_data.get("xp", 0)
            )
            db.add(week_progress)
        
        db.commit()
        return True
    else:
        # Not all modules completed - update counts but don't mark as completed
        if week_progress:
            week_progress.completed_modules_count = completed_count
            week_progress.total_modules_count = total_modules
            if week_progress.is_completed and completed_count < total_modules:
                # Week was previously completed but now has incomplete modules
                week_progress.is_completed = False
                week_progress.completed_at = None
            db.commit()
        else:
            week_progress = WeekProgress(
                learner_id=learner_id,
                learning_plan_id=learning_plan_id,
                week_number=week_number,
                is_completed=False,
                completed_modules_count=completed_count,
                total_modules_count=total_modules,
                xp_earned=0
            )
            db.add(week_progress)
            db.commit()
        
        return False


async def _update_learner_progress(
    db: Session,
    learner_id: int,
    learning_plan_id: int
):
    """Update learner's overall progress (XP, completed modules, etc.)"""
    # Get all completed modules
    completed_modules = db.query(ModuleProgress).filter(
        ModuleProgress.learner_id == learner_id,
        ModuleProgress.learning_plan_id == learning_plan_id,
        ModuleProgress.is_completed == True
    ).all()
    
    # Get all completed weeks
    completed_weeks = db.query(WeekProgress).filter(
        WeekProgress.learner_id == learner_id,
        WeekProgress.learning_plan_id == learning_plan_id,
        WeekProgress.is_completed == True
    ).all()
    
    # Calculate total XP earned
    total_xp = sum(wp.xp_earned for wp in completed_weeks)
    
    # Get or create learner progress record
    progress = db.query(Progress).filter(
        Progress.learner_id == learner_id
    ).first()
    
    if progress:
        # Update existing progress
        completed_module_names = [mp.module_name for mp in completed_modules]
        progress.completed_modules = completed_module_names
        progress.xp = total_xp
    else:
        # Create new progress record
        completed_module_names = [mp.module_name for mp in completed_modules]
        progress = Progress(
            learner_id=learner_id,
            completed_modules=completed_module_names,
            xp=total_xp,
            streak=0
        )
        db.add(progress)
    
    db.commit()

