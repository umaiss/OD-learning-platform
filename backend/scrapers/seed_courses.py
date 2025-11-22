"""
Script to seed the course database with popular courses and create embeddings
Run this after initializing the database to populate courses
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from db.database import get_db
from scrapers.course_scraper import CourseScraper
from core.vector_utils import create_embeddings_for_content
from db.models import Course


async def create_course_embeddings(db):
    """Create vector embeddings for all courses that don't have them yet"""
    courses = db.query(Course).all()
    
    print(f"\nCreating embeddings for {len(courses)} courses...")
    
    for course in courses:
        try:
            # Check if embedding already exists
            from db.vector import VectorEmbedding
            existing = db.query(VectorEmbedding).filter(
                VectorEmbedding.course_id == course.id
            ).first()
            
            if existing:
                print(f"  ✓ Embedding already exists for: {course.title}")
                continue
            
            # Create text representation for embedding
            course_text = f"{course.title} {course.description or ''} {' '.join(course.topics or [])}"
            
            # Create embedding
            await create_embeddings_for_content(
                db=db,
                text=course_text,
                content_type="course",
                course_id=course.id
            )
            
            print(f"  ✓ Created embedding for: {course.title}")
        except Exception as e:
            print(f"  ✗ Failed to create embedding for {course.title}: {str(e)}")


async def main():
    """Main function to seed courses and create embeddings"""
    print("Starting course database seeding...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Seed popular courses
        print("\n1. Seeding popular courses...")
        scraper = CourseScraper(db)
        
        # Popular free courses
        popular_courses = [
            {
                'title': 'The Complete JavaScript Course 2024',
                'url': 'https://www.udemy.com/course/the-complete-javascript-course/',
                'platform': 'udemy',
                'description': 'Master JavaScript with the most complete course on the market',
                'topics': ['javascript', 'web development', 'programming'],
                'difficulty': 'intermediate',
                'rating': 4.7,
                'duration_hours': 69,
                'price': 0.0,
                'instructor': 'Jonas Schmedtmann',
                'is_verified': True
            },
            {
                'title': 'React - The Complete Guide',
                'url': 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/',
                'platform': 'udemy',
                'description': 'Dive in and learn React from scratch',
                'topics': ['react', 'javascript', 'frontend', 'web development'],
                'difficulty': 'intermediate',
                'rating': 4.6,
                'duration_hours': 50,
                'price': 0.0,
                'instructor': 'Maximilian Schwarzmüller',
                'is_verified': True
            },
            {
                'title': 'Python for Everybody',
                'url': 'https://www.coursera.org/specializations/python',
                'platform': 'coursera',
                'description': 'Learn to Program and Analyze Data with Python',
                'topics': ['python', 'programming', 'data science'],
                'difficulty': 'beginner',
                'rating': 4.8,
                'duration_hours': 100,
                'price': 0.0,
                'instructor': 'Charles Severance',
                'is_verified': True
            },
            {
                'title': 'Machine Learning by Andrew Ng',
                'url': 'https://www.coursera.org/learn/machine-learning',
                'platform': 'coursera',
                'description': 'Machine Learning course by Stanford University',
                'topics': ['machine learning', 'ai', 'data science', 'python'],
                'difficulty': 'intermediate',
                'rating': 4.9,
                'duration_hours': 60,
                'price': 0.0,
                'instructor': 'Andrew Ng',
                'is_verified': True
            },
            {
                'title': 'freeCodeCamp - Full Stack Web Development',
                'url': 'https://www.freecodecamp.org/learn',
                'platform': 'freecodecamp',
                'description': 'Learn to code for free',
                'topics': ['web development', 'javascript', 'html', 'css', 'full stack'],
                'difficulty': 'beginner',
                'rating': 4.8,
                'duration_hours': 300,
                'price': 0.0,
                'instructor': 'freeCodeCamp',
                'is_verified': True
            },
        ]
        
        added_count = 0
        for course_data in popular_courses:
            try:
                course = scraper.add_course_manual(**course_data)
                if course:
                    added_count += 1
                    print(f"  ✓ Added course: {course.title}")
            except Exception as e:
                print(f"  ✗ Failed to add course {course_data['title']}: {str(e)}")
        
        # Create embeddings for all courses
        print("\n2. Creating vector embeddings...")
        await create_course_embeddings(db)
        
        print(f"\n✓ Course seeding complete! Added {added_count} courses.")
    except Exception as e:
        print(f"\n✗ Error seeding courses: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())

