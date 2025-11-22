"""
API endpoints for course management and suggestions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from db.database import get_db
from db.models import Course, Learner
from agents.course_suggester import CourseSuggester, LearningMaterial
from core.dependencies import get_current_user, verify_learner_access_helper
from scrapers.course_scraper import CourseScraper

router = APIRouter(prefix="/courses", tags=["courses"])
course_suggester = CourseSuggester()


class SuggestCoursesRequest(BaseModel):
    """Request to suggest courses for a module"""
    learner_id: int
    module_name: str
    module_description: str
    skill_level: Optional[str] = "intermediate"  # beginner, intermediate, advanced
    limit: Optional[int] = 5


class SuggestCoursesResponse(BaseModel):
    """Response with course suggestions"""
    learner_id: int
    module_name: str
    suggestions: List[LearningMaterial]
    message: str = "Course suggestions generated successfully"


class AddCourseRequest(BaseModel):
    """Request to manually add a course"""
    url: str
    topics: Optional[List[str]] = None
    difficulty: Optional[str] = "intermediate"


class AddCourseResponse(BaseModel):
    """Response after adding a course"""
    course_id: int
    title: str
    url: str
    platform: str
    message: str = "Course added successfully"


@router.post("/suggest", response_model=SuggestCoursesResponse, status_code=status.HTTP_200_OK)
async def suggest_courses(
    request: SuggestCoursesRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Suggest courses for a module using hybrid approach (local DB + LLM) (requires authentication)"""
    try:
        # Verify user has access to this learner
        learner = verify_learner_access_helper(request.learner_id, current_user, db)
        
        # Get suggestions
        suggestions = await course_suggester.suggest_courses_for_module(
            db=db,
            module_name=request.module_name,
            module_description=request.module_description,
            skill_level=request.skill_level,
            limit=request.limit
        )
        
        return SuggestCoursesResponse(
            learner_id=request.learner_id,
            module_name=request.module_name,
            suggestions=suggestions
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error suggesting courses: {str(e)}"
        )


@router.post("/add", response_model=AddCourseResponse, status_code=status.HTTP_201_CREATED)
async def add_course(
    request: AddCourseRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a course to the database from a URL (requires authentication)"""
    try:
        # Only managers can add courses (or you can allow all authenticated users)
        if current_user.role != "manager":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only managers can add courses"
            )
        
        scraper = CourseScraper(db)
        course = scraper.add_course_from_url(
            url=request.url,
            topics=request.topics,
            difficulty=request.difficulty
        )
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add course. Please check the URL."
            )
        
        # Create embedding for the course (async)
        try:
            from core.vector_utils import create_embeddings_for_content
            course_text = f"{course.title} {course.description or ''} {' '.join(course.topics or [])}"
            await create_embeddings_for_content(
                db=db,
                text=course_text,
                content_type="course",
                course_id=course.id
            )
        except Exception as e:
            print(f"Warning: Failed to create embedding for course {course.id}: {str(e)}")
        
        return AddCourseResponse(
            course_id=course.id,
            title=course.title,
            url=course.url,
            platform=course.platform
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding course: {str(e)}"
        )


@router.get("/search", status_code=status.HTTP_200_OK)
async def search_courses(
    query: str,
    platform: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 10,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search courses in the database (requires authentication)"""
    try:
        # Build query
        courses_query = db.query(Course)
        
        if platform:
            courses_query = courses_query.filter(Course.platform == platform)
        
        if difficulty:
            courses_query = courses_query.filter(Course.difficulty == difficulty)
        
        # Simple text search in title and description
        if query:
            courses_query = courses_query.filter(
                (Course.title.ilike(f"%{query}%")) |
                (Course.description.ilike(f"%{query}%"))
            )
        
        courses = courses_query.limit(limit).all()
        
        return {
            "courses": [
                {
                    "id": course.id,
                    "title": course.title,
                    "url": course.url,
                    "platform": course.platform,
                    "description": course.description,
                    "rating": course.rating,
                    "difficulty": course.difficulty,
                    "duration_hours": course.duration_hours,
                    "is_free": course.is_free,
                    "is_verified": course.is_verified
                }
                for course in courses
            ],
            "count": len(courses)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching courses: {str(e)}"
        )

