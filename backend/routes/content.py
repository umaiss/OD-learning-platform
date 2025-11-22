from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from db.database import get_db
from db.models import Content
from agents.content_generator import ContentGenerator

router = APIRouter(prefix="/content", tags=["content"])
content_generator = ContentGenerator()


class ContentCreate(BaseModel):
    title: str
    content_type: str
    content: str
    skill_tags: Optional[List[str]] = None
    difficulty: Optional[str] = None
    meta_data: Optional[dict] = None


class ContentResponse(BaseModel):
    id: int
    title: str
    content_type: str
    content: str
    skill_tags: Optional[List[str]]
    difficulty: Optional[str]
    metadata: Optional[dict]
    
    class Config:
        from_attributes = True


class GenerateContentRequest(BaseModel):
    topic: str
    content_type: str = "article"
    difficulty: str = "intermediate"
    length: str = "medium"
    context: Optional[dict] = None


@router.post("/generate", response_model=dict)
async def generate_content(request: GenerateContentRequest):
    """Generate learning content"""
    try:
        content = await content_generator.generate_content(
            topic=request.topic,
            content_type=request.content_type,
            difficulty=request.difficulty,
            length=request.length,
            context=request.context
        )
        return {"content": content}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating content: {str(e)}"
        )


@router.post("/generate-exercise", response_model=dict)
async def generate_exercise(
    skill: str,
    difficulty: str = "intermediate"
):
    """Generate a practice exercise"""
    try:
        result = await content_generator.generate_exercise(
            skill=skill,
            difficulty=difficulty
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating exercise: {str(e)}"
        )


@router.post("/generate-quiz", response_model=dict)
async def generate_quiz(
    topic: str,
    num_questions: int = 5,
    difficulty: str = "intermediate"
):
    """Generate a quiz"""
    try:
        result = await content_generator.generate_quiz(
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quiz: {str(e)}"
        )


@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content: ContentCreate,
    db: Session = Depends(get_db)
):
    """Create new content"""
    content_dict = content.dict()
    if content_dict.get("skill_tags"):
        content_dict["skill_tags"] = content_dict["skill_tags"]
    
    db_content = Content(**content_dict)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content


@router.get("/", response_model=List[ContentResponse])
async def get_all_content(
    skip: int = 0,
    limit: int = 100,
    content_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all content with optional filters"""
    query = db.query(Content)
    
    if content_type:
        query = query.filter(Content.content_type == content_type)
    if difficulty:
        query = query.filter(Content.difficulty == difficulty)
    
    content_list = query.offset(skip).limit(limit).all()
    return content_list


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific content item"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content: ContentCreate,
    db: Session = Depends(get_db)
):
    """Update content"""
    db_content = db.query(Content).filter(Content.id == content_id).first()
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    for key, value in content.dict().items():
        setattr(db_content, key, value)
    
    db.commit()
    db.refresh(db_content)
    return db_content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """Delete content"""
    db_content = db.query(Content).filter(Content.id == content_id).first()
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    db.delete(db_content)
    db.commit()
    return None

