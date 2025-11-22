from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Optional
from db.database import get_db
from db.models import Learner, LearningPlan, ChatMessage
from agents.chatbot import ChatbotAgent

router = APIRouter(prefix="/chatbot", tags=["chatbot"])
chatbot = ChatbotAgent()


class ChatRequest(BaseModel):
    learner_id: int
    message: str
    conversation_history: Optional[List[Dict]] = None


class ChatResponse(BaseModel):
    learner_id: int
    message: str
    response: str
    message_id: int
    session_id: Optional[str] = None


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat with SkillPilot AI Coach"""
    try:
        # Verify learner exists
        learner = db.query(Learner).filter(Learner.id == request.learner_id).first()
        if not learner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learner with id {request.learner_id} not found"
            )
        
        # Get learner's skill map and learning plan
        skill_map = learner.skill_map or {}
        
        # Get the most recent learning plan
        learning_plan = db.query(LearningPlan).filter(
            LearningPlan.learner_id == request.learner_id
        ).order_by(LearningPlan.created_at.desc()).first()
        
        learning_plan_dict = None
        if learning_plan:
            learning_plan_dict = learning_plan.plan_json
        
        # Generate session ID (simple implementation)
        session_id = f"learner_{request.learner_id}_session"
        
        # Call the agent
        response_text = await chatbot.chat_with_context(
            message=request.message,
            skill_map=skill_map,
            learning_plan=learning_plan_dict,
            conversation_history=request.conversation_history,
            db=db
        )
        
        # Save user message (user_id is nullable, we use session_id for tracking)
        user_message = ChatMessage(
            user_id=None,  # ChatMessage uses user_id from users table, we track by session_id
            session_id=session_id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.flush()  # Get the ID
        
        # Save assistant response
        assistant_message = ChatMessage(
            user_id=None,  # ChatMessage uses user_id from users table, we track by session_id
            session_id=session_id,
            role="assistant",
            content=response_text
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        return ChatResponse(
            learner_id=request.learner_id,
            message=request.message,
            response=response_text,
            message_id=assistant_message.id,
            session_id=session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat: {str(e)}"
        )

