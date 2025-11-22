from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Date, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


# Association table for Learner-Mentor many-to-many relationship
# Must be defined before User and Learner models that reference it
learner_mentor_association = Table(
    'learner_mentors',
    Base.metadata,
    Column('learner_id', Integer, ForeignKey('learners.id'), primary_key=True),
    Column('mentor_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now()),
    Column('is_active', Boolean, default=True)
)


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)  # Hashed password
    role = Column(String, nullable=False, index=True)  # learner, manager, mentor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    learner = relationship("Learner", back_populates="user", uselist=False, cascade="all, delete-orphan")
    mentored_learners = relationship(
        "Learner",
        secondary=learner_mentor_association,
        back_populates="mentors"
    )
    skill_profiles = relationship("SkillProfile", back_populates="user")
    learning_paths = relationship("LearningPath", back_populates="user")
    missions = relationship("Mission", back_populates="user")
    progress_records = relationship("UserProgress", back_populates="user")


class SkillProfile(Base):
    """Skill profile model"""
    __tablename__ = "skill_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String, nullable=False, index=True)
    skill_level = Column(String, nullable=False)  # beginner, intermediate, advanced
    description = Column(Text)
    meta_data = Column(JSON)  # Additional skill data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="skill_profiles")


class LearningPath(Base):
    """Learning path model"""
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    skill_goal = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)  # beginner, intermediate, advanced
    estimated_duration = Column(Integer)  # in hours
    status = Column(String, default="active")  # active, completed, paused
    meta_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="learning_paths")
    modules = relationship("Module", back_populates="learning_path", cascade="all, delete-orphan")


class Module(Base):
    """Module model for learning path modules"""
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)
    content = Column(Text)
    meta_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    learning_path = relationship("LearningPath", back_populates="modules")


class Content(Base):
    """Content model for generated learning content"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # article, video, exercise, quiz
    content = Column(Text, nullable=False)
    skill_tags = Column(JSON)  # List of related skills
    difficulty = Column(String)
    meta_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Mission(Base):
    """Mission model for gamified learning tasks"""
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    mission_type = Column(String, nullable=False)  # practice, challenge, project
    difficulty = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    points = Column(Integer, default=0)
    meta_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="missions")


class UserProgress(Base):
    """User progress tracking model (for general entity-based progress)"""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entity_type = Column(String, nullable=False)  # learning_path, mission, module
    entity_id = Column(Integer, nullable=False)
    completion_percentage = Column(Float, default=0.0)
    time_spent = Column(Integer, default=0)  # in minutes
    meta_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress_records")


class ChatMessage(Base):
    """Chat message model for chatbot interactions"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String, index=True)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    meta_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# New Learner-focused models

class Learner(Base):
    """Learner model for learning platform users"""
    __tablename__ = "learners"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    professional_role = Column(String, nullable=False)  # e.g., "developer", "designer", "manager"
    experience_years = Column(Integer, default=0)
    skill_map = Column(JSON)  # JSON object mapping skills to levels
    strengths = Column(Text)  # Text description of strengths
    gaps = Column(Text)  # Text description of skill gaps
    ai_analysis = Column(Text)  # AI analysis and remarks from profile generation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="learner")
    mentors = relationship(
        "User",
        secondary=learner_mentor_association,
        back_populates="mentored_learners"
    )
    learning_plans = relationship("LearningPlan", back_populates="learner", cascade="all, delete-orphan")
    generated_content = relationship("GeneratedContent", back_populates="learner", cascade="all, delete-orphan")
    daily_missions = relationship("DailyMission", back_populates="learner", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="learner", cascade="all, delete-orphan")


class LearningPlan(Base):
    """Learning plan model storing personalized learning paths"""
    __tablename__ = "learning_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False, index=True)
    plan_json = Column(JSON, nullable=False)  # JSON structure of the learning plan
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    learner = relationship("Learner", back_populates="learning_plans")


class GeneratedContent(Base):
    """Generated learning content model"""
    __tablename__ = "generated_content"
    
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False, index=True)
    module_name = Column(String, nullable=False)
    lesson_text = Column(Text, nullable=False)  # The main lesson content
    quiz_json = Column(JSON)  # JSON structure for quiz questions and answers
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    learner = relationship("Learner", back_populates="generated_content")


class DailyMission(Base):
    """Daily mission model for gamified learning"""
    __tablename__ = "daily_missions"
    
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False, index=True)
    missions_json = Column(JSON, nullable=False)  # JSON array of mission objects
    xp = Column(Integer, default=0)  # Experience points earned
    streak = Column(Integer, default=0)  # Current streak count
    date = Column(Date, nullable=False, index=True)  # Date of the mission
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    learner = relationship("Learner", back_populates="daily_missions")


class Progress(Base):
    """Learner progress tracking model"""
    __tablename__ = "learner_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"), nullable=False, index=True)
    completed_modules = Column(JSON)  # JSON array of completed module IDs/names
    xp = Column(Integer, default=0)  # Total experience points
    streak = Column(Integer, default=0)  # Current learning streak
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    learner = relationship("Learner", back_populates="progress_records")

