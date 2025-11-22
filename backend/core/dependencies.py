"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from db.database import get_db
from db.models import User, Learner
from core.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (additional check for active status)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


async def get_current_learner(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Learner:
    """Get the learner profile for the current user"""
    if current_user.role != "learner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available for learners"
        )
    
    learner = db.query(Learner).filter(Learner.user_id == current_user.id).first()
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found. Please complete your profile setup."
        )
    
    return learner


def require_role(allowed_roles: list[str]):
    """Dependency factory to require specific roles"""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


def verify_learner_access_helper(
    learner_id: int,
    current_user: User,
    db: Session
) -> Learner:
    """
    Helper function to verify that the current user has access to the specified learner.
    - Learners can only access their own data
    - Managers can access any learner's data
    - Mentors can only access learners assigned to them
    
    Returns:
        Learner: The learner object if access is granted
    
    Raises:
        HTTPException: If access is denied
    """
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with id {learner_id} not found"
        )
    
    # Managers have access to all learners
    if current_user.role == "manager":
        return learner
    
    # Learners can only access their own data
    if current_user.role == "learner":
        if learner.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own learner data"
            )
        return learner
    
    # Mentors can only access learners assigned to them
    if current_user.role == "mentor":
        from db.models import learner_mentor_association
        from sqlalchemy import and_
        
        assignment = db.query(learner_mentor_association).filter(
            and_(
                learner_mentor_association.c.learner_id == learner_id,
                learner_mentor_association.c.mentor_id == current_user.id,
                learner_mentor_association.c.is_active == True
            )
        ).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this learner. The learner must be assigned to you."
            )
        return learner
    
    # Unknown role
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )
