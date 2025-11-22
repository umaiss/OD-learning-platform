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
from db.models import Learner, Progress, Base


def create_demo_learner(db: Session) -> Learner:
    """
    Create a demo learner with sample skill map
    
    Args:
        db: Database session
        
    Returns:
        Learner: Created learner instance
    """
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
    
    # Check if demo learner already exists
    existing_learner = db.query(Learner).filter(Learner.name == "Demo Learner").first()
    if existing_learner:
        print(f"Demo learner already exists with ID: {existing_learner.id}")
        # Update existing learner
        existing_learner.role = "software engineer"
        existing_learner.experience_years = 3
        existing_learner.skill_map = skill_map
        existing_learner.strengths = strengths
        existing_learner.gaps = gaps
        db.commit()
        db.refresh(existing_learner)
        return existing_learner
    
    # Create new learner
    learner = Learner(
        name="Demo Learner",
        role="software engineer",
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


def seed_database():
    """
    Main function to seed the database with demo data
    """
    print("Starting database seeding...")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create demo learner
        print("\n1. Creating demo learner...")
        learner = create_demo_learner(db)
        print(f"   Name: {learner.name}")
        print(f"   Role: {learner.role}")
        print(f"   Experience: {learner.experience_years} years")
        print(f"   Skills: {len(learner.skill_map)} skills mapped")
        
        # Display skill map
        print("\n   Skill Map:")
        for skill, level in learner.skill_map.items():
            print(f"     - {skill}: {level}")
        
        # Create sample progress
        print("\n2. Creating sample progress...")
        progress = create_sample_progress(db, learner.id)
        
        print("\n" + "=" * 50)
        print("Database seeding completed successfully!")
        print(f"\nDemo Learner ID: {learner.id}")
        print(f"Progress Record ID: {progress.id}")
        print("\nYou can now use this learner ID to test the API endpoints.")
        
    except Exception as e:
        print(f"\nError seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

