"""
Authentication routes for signup and login
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional
from db.database import get_db
from db.models import User, Learner, learner_mentor_association
from core.auth import verify_password, get_password_hash, create_access_token
from core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["authentication"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "manager"  # Only manager allowed for public signup


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str  # learner or mentor (managers create these)
    professional_role: Optional[str] = None  # For learners: developer, designer, etc.
    experience_years: Optional[int] = 0


class SignupResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    message: str = "User created successfully"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    """Sign up a new Manager (only managers can sign up publicly)"""
    # Only allow manager role for public signup
    if request.role.lower() != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can sign up. Please contact a manager to create your account."
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create manager user
    user = User(
        email=request.email,
        name=request.name,
        password_hash=get_password_hash(request.password),
        role="manager",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return SignupResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    # OAuth2PasswordRequestForm uses 'username' field for email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    )


@router.post("/login-json", response_model=TokenResponse)
async def login_json(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login using JSON body (alternative to OAuth2 form)"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    )


@router.post("/create-user", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user (Learner or Mentor) - Only managers can create users"""
    # Only managers can create users
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can create users"
        )
    
    # Validate role (only learner or mentor can be created by managers)
    valid_roles = ["learner", "mentor"]
    if request.role.lower() not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Managers can only create: {', '.join(valid_roles)}"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=request.email,
        name=request.name,
        password_hash=get_password_hash(request.password),
        role=request.role.lower(),
        is_active=True
    )
    db.add(user)
    db.flush()  # Get the user ID
    
    # If role is learner, create learner profile
    if request.role.lower() == "learner":
        learner = Learner(
            user_id=user.id,
            professional_role=request.professional_role or "developer",
            experience_years=request.experience_years or 0
        )
        db.add(learner)
    
    db.commit()
    db.refresh(user)
    
    return SignupResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role
    )


@router.post("/assign-mentor", status_code=status.HTTP_200_OK)
async def assign_mentor_to_learner(
    learner_id: int,
    mentor_id: int,
    current_user: User = Depends(require_role(["manager"])),
    db: Session = Depends(get_db)
):
    """Assign a mentor to a learner (Manager only)"""
    # Verify learner exists
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner not found"
        )
    
    # Verify mentor exists and is a mentor
    mentor = db.query(User).filter(
        User.id == mentor_id,
        User.role == "mentor"
    ).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found or user is not a mentor"
        )
    
    # Check if already assigned
    existing = db.execute(
        select(learner_mentor_association).where(
            learner_mentor_association.c.learner_id == learner_id,
            learner_mentor_association.c.mentor_id == mentor_id
        )
    ).first()
    
    if existing:
        # Reactivate if inactive
        db.execute(
            learner_mentor_association.update().where(
                learner_mentor_association.c.learner_id == learner_id,
                learner_mentor_association.c.mentor_id == mentor_id
            ).values(is_active=True)
        )
        message = "Mentor assignment reactivated"
    else:
        # Create new assignment
        db.execute(
            learner_mentor_association.insert().values(
                learner_id=learner_id,
                mentor_id=mentor_id,
                is_active=True
            )
        )
        message = "Mentor assigned successfully"
    
    db.commit()
    return {"message": message, "learner_id": learner_id, "mentor_id": mentor_id}


@router.delete("/assign-mentor/{learner_id}/{mentor_id}", status_code=status.HTTP_200_OK)
async def remove_mentor_from_learner(
    learner_id: int,
    mentor_id: int,
    current_user: User = Depends(require_role(["manager"])),
    db: Session = Depends(get_db)
):
    """Remove a mentor from a learner (Manager only)"""
    # Deactivate the assignment instead of deleting
    result = db.execute(
        learner_mentor_association.update().where(
            learner_mentor_association.c.learner_id == learner_id,
            learner_mentor_association.c.mentor_id == mentor_id
        ).values(is_active=False)
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor assignment not found"
        )
    
    db.commit()
    return {"message": "Mentor removed from learner"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        is_active=current_user.is_active
    )

