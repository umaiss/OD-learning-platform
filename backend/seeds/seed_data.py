"""
Seed data script for populating the database with demo data
"""
import sys
from pathlib import Path
from datetime import date

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from db.models import Learner, Progress, User, Base, learner_mentor_association
from core.auth import get_password_hash


def create_demo_learner(db: Session) -> Learner:
    """
    Create a demo learner with sample skill map
    
    Args:
        db: Database session
        
    Returns:
        Learner: Created learner instance
    """
    # Check if demo learner user already exists
    existing_user = db.query(User).filter(User.email == "learner@demo.com").first()
    if existing_user and existing_user.learner:
        print(f"Demo learner already exists with ID: {existing_user.learner.id}")
        learner = existing_user.learner
        # Update existing learner
        learner.professional_role = "software engineer"
        learner.experience_years = 3
        learner.skill_map = {
            "Python": "intermediate",
            "JavaScript": "advanced",
            "React": "intermediate",
            "Docker": "beginner",
            "Kubernetes": "beginner",
            "PostgreSQL": "intermediate",
            "FastAPI": "intermediate",
            "TypeScript": "beginner",
            "AWS": "beginner",
            "CI/CD": "beginner"
        }
        learner.strengths = """Strong foundation in Python and JavaScript programming.
Experienced with React for frontend development.
Good understanding of database concepts with PostgreSQL.
Familiar with FastAPI for building REST APIs.
Solid problem-solving and debugging skills."""
        learner.gaps = """Need to learn containerization with Docker.
Kubernetes orchestration is a new area to explore.
TypeScript would improve code quality and maintainability.
Cloud infrastructure knowledge (AWS) needs development.
CI/CD pipelines and DevOps practices are areas for growth."""
        db.commit()
        db.refresh(learner)
        return learner
    
    # Sample skill map
    skill_map = {
        "Python": "intermediate",
        "JavaScript": "advanced",
        "React": "intermediate",
        "Docker": "beginner",
        "Kubernetes": "beginner",
        "PostgreSQL": "intermediate",
        "FastAPI": "intermediate",
        "TypeScript": "beginner",
        "AWS": "beginner",
        "CI/CD": "beginner"
    }
    
    # Sample strengths and gaps
    strengths = """Strong foundation in Python and JavaScript programming.
Experienced with React for frontend development.
Good understanding of database concepts with PostgreSQL.
Familiar with FastAPI for building REST APIs.
Solid problem-solving and debugging skills."""
    
    gaps = """Need to learn containerization with Docker.
Kubernetes orchestration is a new area to explore.
TypeScript would improve code quality and maintainability.
Cloud infrastructure knowledge (AWS) needs development.
CI/CD pipelines and DevOps practices are areas for growth."""
    
    # Create learner user first
    learner_user = User(
        email="learner@demo.com",
        name="Demo Learner",
        password_hash=get_password_hash("demo123"),
        role="learner",
        is_active=True
    )
    db.add(learner_user)
    db.flush()  # Get the user ID
    
    # Create learner profile
    learner = Learner(
        user_id=learner_user.id,
        professional_role="software engineer",
        experience_years=3,
        skill_map=skill_map,
        strengths=strengths,
        gaps=gaps
    )
    
    db.add(learner)
    db.commit()
    db.refresh(learner)
    
    print(f"Created demo learner with ID: {learner.id}")
    return learner


def create_demo_mentor(db: Session) -> User:
    """
    Create a demo mentor user
    """
    email = "mentor@demo.com"
    password = "demo123"
    name = "Demo Mentor"
    role = "mentor"

    existing_mentor = db.query(User).filter(User.email == email).first()
    if existing_mentor:
        print(f"Demo mentor already exists with ID: {existing_mentor.id}")
        return existing_mentor

    user = User(
        email=email,
        name=name,
        password_hash=get_password_hash(password),
        role=role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"Created demo mentor with ID: {user.id}")
    print(f"   Email: {email}")
    print(f"   Name: {name}")
    print(f"   Role: {role}")
    print(f"   Password: {password}")  # For demo purposes, show password

    return user


def assign_mentor_to_learner(db: Session, learner_id: int, mentor_id: int):
    """
    Assign a mentor to a learner
    """
    # Check if already assigned
    from sqlalchemy import select
    existing = db.execute(
        select(learner_mentor_association).where(
            learner_mentor_association.c.learner_id == learner_id,
            learner_mentor_association.c.mentor_id == mentor_id
        )
    ).first()

    if existing:
        print(f"Mentor {mentor_id} already assigned to learner {learner_id}")
        return

    # Create new assignment
    db.execute(
        learner_mentor_association.insert().values(
            learner_id=learner_id,
            mentor_id=mentor_id,
            is_active=True
        )
    )
    db.commit()
    print(f"Assigned mentor {mentor_id} to learner {learner_id}")


def create_sample_progress(db: Session, learner_id: int) -> Progress:
    """
    Create sample progress record for a learner
    
    Args:
        db: Database session
        learner_id: ID of the learner
        
    Returns:
        Progress: Created progress instance
    """
    # Sample completed modules
    completed_modules = [
        "Python Basics",
        "JavaScript Fundamentals",
        "React Components",
        "REST API Design"
    ]
    
    # Check if progress already exists
    existing_progress = db.query(Progress).filter(
        Progress.learner_id == learner_id
    ).first()
    
    if existing_progress:
        print(f"Progress record already exists for learner {learner_id}")
        # Update existing progress
        existing_progress.completed_modules = completed_modules
        existing_progress.xp = 250
        existing_progress.streak = 7
        db.commit()
        db.refresh(existing_progress)
        return existing_progress
    
    # Create new progress record
    progress = Progress(
        learner_id=learner_id,
        completed_modules=completed_modules,
        xp=250,
        streak=7
    )
    
    db.add(progress)
    db.commit()
    db.refresh(progress)
    
    print(f"Created progress record with ID: {progress.id}")
    print(f"  - Completed modules: {len(completed_modules)}")
    print(f"  - Total XP: {progress.xp}")
    print(f"  - Current streak: {progress.streak} days")
    
    return progress


def create_demo_manager(db: Session) -> User:
    """
    Create a demo manager user
    
    Args:
        db: Database session
        
    Returns:
        User: Created manager user
    """
    # Check if manager already exists
    existing_manager = db.query(User).filter(User.email == "manager@demo.com").first()
    if existing_manager:
        print(f"Demo manager already exists with ID: {existing_manager.id}")
        return existing_manager
    
    # Create manager user
    manager = User(
        email="manager@demo.com",
        name="Demo Manager",
        password_hash=get_password_hash("demo123"),
        role="manager",
        is_active=True
    )
    
    db.add(manager)
    db.commit()
    db.refresh(manager)
    
    print(f"Created demo manager with ID: {manager.id}")
    return manager


def seed_database():
    """
    Main function to seed the database with demo data
    """
    print("Starting database seeding...")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create demo manager
        print("\n0. Creating demo manager...")
        manager = create_demo_manager(db)
        print(f"   Email: {manager.email}")
        print(f"   Name: {manager.name}")
        print(f"   Role: {manager.role}")
        print(f"   Password: demo123")
        
        # Create demo mentor
        print("\n1. Creating demo mentor...")
        mentor = create_demo_mentor(db)
        print(f"   Email: {mentor.email}")
        print(f"   Name: {mentor.name}")
        print(f"   Role: {mentor.role}")
        print(f"   Password: demo123")
        
        # Create demo learner
        print("\n2. Creating demo learner...")
        learner = create_demo_learner(db)
        print(f"   Email: {learner.user.email}")
        print(f"   Name: {learner.user.name}")
        print(f"   Professional Role: {learner.professional_role}")
        print(f"   Experience: {learner.experience_years} years")
        print(f"   Skills: {len(learner.skill_map) if learner.skill_map else 0} skills mapped")
        
        # Display skill map
        print("\n   Skill Map:")
        for skill, level in learner.skill_map.items():
            print(f"     - {skill}: {level}")
        
        # Assign mentor to learner
        print("\n3. Assigning mentor to learner...")
        assign_mentor_to_learner(db, learner.id, mentor.id)
        
        # Create sample progress
        print("\n4. Creating sample progress...")
        progress = create_sample_progress(db, learner.id)
        
        print("\n" + "=" * 50)
        print("Database seeding completed successfully!")
        print("\n" + "=" * 50)
        print("DEMO CREDENTIALS:")
        print("=" * 50)
        print("MANAGER:")
        print(f"  Email: {manager.email}")
        print(f"  Password: demo123")
        print(f"  Role: {manager.role}")
        print("\nMENTOR:")
        print(f"  Email: {mentor.email}")
        print(f"  Password: demo123")
        print(f"  Role: {mentor.role}")
        print("\nLEARNER:")
        print(f"  Email: {learner.user.email}")
        print(f"  Password: demo123")
        print(f"  Role: learner")
        print("=" * 50)
        print(f"\nDemo Manager ID: {manager.id}")
        print(f"Demo Mentor ID: {mentor.id}")
        print(f"Demo Learner ID: {learner.id}")
        print(f"Progress Record ID: {progress.id}")
        print(f"\nMentor-Mentee Relationship: Mentor {mentor.id} -> Learner {learner.id}")
        print("\nYou can now use these credentials to test the API endpoints.")
        
    except Exception as e:
        print(f"\nError seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

