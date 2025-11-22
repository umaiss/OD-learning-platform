from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Optional
from db.database import get_db
from db.models import Learner, LearningPlan, User
from agents.learning_path import LearningPathGenerator, LearningPathOutput, ModuleInfo, WeeklyGoal
from agents.course_suggester import CourseSuggester
from core.dependencies import get_current_user, verify_learner_access_helper
from core.vector_utils import create_embeddings_for_content
import json

router = APIRouter(prefix="/learning-path", tags=["learning-path"])
path_generator = LearningPathGenerator()
course_suggester = CourseSuggester()


class GenerateLearningPathRequest(BaseModel):
    learner_id: int
    skill_map: Optional[Dict[str, str]] = None  # Optional: will use saved profile if not provided
    experience: Optional[int] = None  # Optional: will use saved profile if not provided
    role: Optional[str] = None  # Optional: will use saved profile if not provided
    learning_goals: Optional[str] = None  # Optional: will use saved profile if not provided


class WeeklyGoalResponse(BaseModel):
    """Weekly goal response structure"""
    week: int
    goals: List[str]
    modules: List[Dict[str, str]]  # List of {name, description}
    xp: int
    milestones: List[str]


class GenerateLearningPathResponse(BaseModel):
    learner_id: int
    learning_plan_id: int
    duration_weeks: int
    weekly_goals: List[WeeklyGoalResponse]  # Structured weekly goals with modules, XP, and milestones
    total_xp: int  # Total XP for the entire learning path
    message: str = "Learning path generated and saved successfully"


class SaveLearningPathRequest(BaseModel):
    learner_id: int
    duration_weeks: int
    weekly_goals: List[WeeklyGoalResponse]  # Structured weekly goals with modules, XP, and milestones
    total_xp: Optional[int] = None  # Optional: will be calculated if not provided


class SaveLearningPathResponse(BaseModel):
    learner_id: int
    learning_plan_id: int
    message: str = "Learning path saved successfully"


@router.post("/generate", response_model=GenerateLearningPathResponse, status_code=status.HTTP_201_CREATED)
async def generate_learning_path(
    request: GenerateLearningPathRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a personalized learning path for a learner (requires authentication)
    
    If skill_map, experience, or role are not provided, they will be fetched from the learner's saved profile.
    """
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Use provided values or fall back to saved profile data
        skill_map = request.skill_map
        experience = request.experience
        role = request.role
        learning_goals = request.learning_goals
        
        # If not provided, try to get from saved profile
        if skill_map is None:
            if learner.skill_map:
                skill_map = learner.skill_map
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="skill_map is required. Either provide it in the request or generate a profile first using /api/v1/profile/generate"
                )
        
        if experience is None:
            experience = learner.experience_years or 0
        
        if role is None:
            role = learner.professional_role or "developer"
        
        if learning_goals is None:
            learning_goals = learner.learning_goals or ""
        
        # Call the agent
        result: LearningPathOutput = await path_generator.generate_learning_path_plan(
            skill_map=skill_map,
            experience=experience,
            role=role,
            learning_goals=learning_goals
        )
        
        # Convert weekly goals to dict format for JSON storage and response
        # Also auto-suggest learning materials for each module
        weekly_goals_dict = []
        total_xp = 0
        
        for weekly_goal in result.weekly_goals:
            # Convert modules to dict format and add course suggestions
            modules_dict = []
            for m in weekly_goal.modules:
                module_dict = {"name": m.name, "description": m.description}
                
                # Auto-suggest learning materials for this module
                try:
                    # Determine skill level from learner's experience
                    skill_level = "beginner" if experience < 2 else ("advanced" if experience > 5 else "intermediate")
                    
                    suggested_courses = await course_suggester.suggest_courses_for_module(
                        db=db,
                        module_name=m.name,
                        module_description=m.description,
                        skill_level=skill_level,
                        limit=3  # Suggest 3 courses per module
                    )
                    
                    # Convert to dict format for JSON storage
                    if suggested_courses:
                        module_dict["learning_materials"] = [
                            {
                                "title": course.title,
                                "url": course.url,
                                "platform": course.platform,
                                "type": course.type or "course",
                                "estimated_hours": course.estimated_hours,
                                "description": course.description
                            }
                            for course in suggested_courses
                        ]
                except Exception as e:
                    # Don't fail if course suggestion fails
                    print(f"Warning: Failed to suggest courses for module {m.name}: {str(e)}")
                    module_dict["learning_materials"] = []
                
                modules_dict.append(module_dict)
            
            # Create weekly goal dict with all required fields
            weekly_goal_dict = {
                "week": weekly_goal.week,
                "goals": weekly_goal.goals,
                "modules": modules_dict,
                "xp": weekly_goal.xp,
                "milestones": weekly_goal.milestones
            }
            weekly_goals_dict.append(weekly_goal_dict)
            
            # Calculate total XP for gamification
            total_xp += weekly_goal.xp
        
        # Create learning plan in database with complete structure
        plan_json = {
            "duration_weeks": result.duration_weeks,
            "weekly_goals": weekly_goals_dict,
            "total_xp": total_xp,  # Total XP for the entire learning path
            "created_at": None  # Will be set by database
        }
        
        learning_plan = LearningPlan(
            learner_id=request.learner_id,
            plan_json=plan_json
        )
        
        db.add(learning_plan)
        db.commit()
        db.refresh(learning_plan)
        
        # Create vector embeddings for the learning plan
        # This enables semantic search in the chatbot
        try:
            # Create a text representation of the learning plan for embedding
            plan_text_parts = [
                f"Learning Path: {role} with {experience} years experience",
                f"Duration: {result.duration_weeks} weeks",
                f"Total XP: {total_xp}"
            ]
            
            if learning_goals:
                plan_text_parts.append(f"Learning Goals: {learning_goals}")
            
            for weekly_goal in result.weekly_goals:
                plan_text_parts.append(f"Week {weekly_goal.week}: {', '.join(weekly_goal.goals)}")
                for module in weekly_goal.modules:
                    plan_text_parts.append(f"  Module: {module.name} - {module.description}")
                if weekly_goal.milestones:
                    plan_text_parts.append(f"  Milestones: {', '.join(weekly_goal.milestones)}")
            
            plan_text = "\n".join(plan_text_parts)
            
            await create_embeddings_for_content(
                db=db,
                text=plan_text,
                content_type="learning_plan",
                learner_id=request.learner_id,
                learning_plan_id=learning_plan.id
            )
        except Exception as e:
            # Don't fail the request if embedding creation fails
            print(f"Warning: Failed to create embeddings for learning plan: {str(e)}")
        
        # Convert to response format
        weekly_goals_response = [
            WeeklyGoalResponse(
                week=wg["week"],
                goals=wg["goals"],
                modules=wg["modules"],
                xp=wg["xp"],
                milestones=wg["milestones"]
            )
            for wg in weekly_goals_dict
        ]
        
        return GenerateLearningPathResponse(
            learner_id=request.learner_id,
            learning_plan_id=learning_plan.id,
            duration_weeks=result.duration_weeks,
            weekly_goals=weekly_goals_response,
            total_xp=total_xp
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating learning path: {str(e)}"
        )


@router.post("/save", response_model=SaveLearningPathResponse, status_code=status.HTTP_201_CREATED)
async def save_learning_path(
    request: SaveLearningPathRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a learning path for a learner (requires authentication)
    
    This endpoint allows you to save a learning path structure that was either:
    - Generated externally
    - Modified from a generated path
    - Created manually
    
    The learning path will be saved to the database and embeddings will be created for semantic search.
    """
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Calculate total XP if not provided
        total_xp = request.total_xp
        if total_xp is None:
            total_xp = sum(weekly_goal.xp for weekly_goal in request.weekly_goals)
        
        # Convert weekly goals to dict format for JSON storage
        weekly_goals_dict = []
        for weekly_goal in request.weekly_goals:
            weekly_goal_dict = {
                "week": weekly_goal.week,
                "goals": weekly_goal.goals,
                "modules": weekly_goal.modules,  # Already a list of dicts
                "xp": weekly_goal.xp,
                "milestones": weekly_goal.milestones
            }
            weekly_goals_dict.append(weekly_goal_dict)
        
        # Create learning plan in database
        plan_json = {
            "duration_weeks": request.duration_weeks,
            "weekly_goals": weekly_goals_dict,
            "total_xp": total_xp,
            "created_at": None  # Will be set by database
        }
        
        learning_plan = LearningPlan(
            learner_id=request.learner_id,
            plan_json=plan_json
        )
        
        db.add(learning_plan)
        db.commit()
        db.refresh(learning_plan)
        
        # Create vector embeddings for the learning plan
        # This enables semantic search in the chatbot
        try:
            # Get learner profile data for context
            role = learner.professional_role or "developer"
            experience = learner.experience_years or 0
            learning_goals = learner.learning_goals or ""
            
            # Create a text representation of the learning plan for embedding
            plan_text_parts = [
                f"Learning Path: {role} with {experience} years experience",
                f"Duration: {request.duration_weeks} weeks",
                f"Total XP: {total_xp}"
            ]
            
            if learning_goals:
                plan_text_parts.append(f"Learning Goals: {learning_goals}")
            
            for weekly_goal in request.weekly_goals:
                plan_text_parts.append(f"Week {weekly_goal.week}: {', '.join(weekly_goal.goals)}")
                for module in weekly_goal.modules:
                    plan_text_parts.append(f"  Module: {module.get('name', 'Unknown')} - {module.get('description', '')}")
                if weekly_goal.milestones:
                    plan_text_parts.append(f"  Milestones: {', '.join(weekly_goal.milestones)}")
            
            plan_text = "\n".join(plan_text_parts)
            
            await create_embeddings_for_content(
                db=db,
                text=plan_text,
                content_type="learning_plan",
                learner_id=request.learner_id,
                learning_plan_id=learning_plan.id
            )
        except Exception as e:
            # Don't fail the request if embedding creation fails
            print(f"Warning: Failed to create embeddings for learning plan: {str(e)}")
        
        return SaveLearningPathResponse(
            learner_id=request.learner_id,
            learning_plan_id=learning_plan.id,
            message="Learning path saved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving learning path: {str(e)}"
        )

