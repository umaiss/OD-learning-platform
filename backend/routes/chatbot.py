from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from agents.chatbot import ChatbotAgent

router = APIRouter(prefix="/chatbot", tags=["chatbot"])
chatbot = ChatbotAgent()


class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    response: str


class QuestionRequest(BaseModel):
    question: str
    topic: Optional[str] = None
    difficulty: Optional[str] = None


class HintRequest(BaseModel):
    problem: str
    user_attempt: Optional[str] = None
    hints_given: int = 0


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the learning assistant"""
    try:
        # Convert Pydantic models to dicts for the agent
        history = None
        if request.conversation_history:
            history = [msg.dict() for msg in request.conversation_history]
        
        response = await chatbot.chat(
            message=request.message,
            conversation_history=history,
            context=request.context
        )
        
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat: {str(e)}"
        )


@router.post("/answer", response_model=dict)
async def answer_question(request: QuestionRequest):
    """Get a detailed answer to a question"""
    try:
        result = await chatbot.answer_question(
            question=request.question,
            topic=request.topic,
            difficulty=request.difficulty
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error answering question: {str(e)}"
        )


@router.post("/hint", response_model=dict)
async def get_hint(request: HintRequest):
    """Get a hint for a problem"""
    try:
        result = await chatbot.provide_hint(
            problem=request.problem,
            user_attempt=request.user_attempt,
            hints_given=request.hints_given
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error providing hint: {str(e)}"
        )

