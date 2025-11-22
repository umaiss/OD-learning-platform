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
        
        # Comprehensive list of popular courses across multiple platforms
        # Note: These are manually curated. For actual scraping, use the scraper methods
        # but be aware that Udemy/Coursera have anti-scraping measures
        popular_courses = [
            # JavaScript & Web Development
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
                'title': 'JavaScript: The Complete Guide',
                'url': 'https://www.udemy.com/course/javascript-the-complete-guide-2020-beginner-advanced/',
                'platform': 'udemy',
                'description': 'Modern JavaScript from the beginning',
                'topics': ['javascript', 'es6', 'web development'],
                'difficulty': 'intermediate',
                'rating': 4.6,
                'duration_hours': 52,
                'price': 0.0,
                'instructor': 'Maximilian Schwarzmüller',
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
                'title': 'Next.js & React - The Complete Guide',
                'url': 'https://www.udemy.com/course/nextjs-react-the-complete-guide/',
                'platform': 'udemy',
                'description': 'Learn Next.js from the ground up',
                'topics': ['nextjs', 'react', 'full stack', 'web development'],
                'difficulty': 'intermediate',
                'rating': 4.7,
                'duration_hours': 45,
                'price': 0.0,
                'instructor': 'Maximilian Schwarzmüller',
                'is_verified': True
            },
            {
                'title': 'Vue.js - The Complete Guide',
                'url': 'https://www.udemy.com/course/vuejs-2-the-complete-guide/',
                'platform': 'udemy',
                'description': 'Vue.js is an awesome JavaScript Framework',
                'topics': ['vuejs', 'javascript', 'frontend'],
                'difficulty': 'intermediate',
                'rating': 4.7,
                'duration_hours': 48,
                'price': 0.0,
                'instructor': 'Maximilian Schwarzmüller',
                'is_verified': True
            },
            {
                'title': 'Angular - The Complete Guide',
                'url': 'https://www.udemy.com/course/the-complete-guide-to-angular-2/',
                'platform': 'udemy',
                'description': 'Master Angular and build awesome applications',
                'topics': ['angular', 'typescript', 'frontend'],
                'difficulty': 'intermediate',
                'rating': 4.6,
                'duration_hours': 34,
                'price': 0.0,
                'instructor': 'Maximilian Schwarzmüller',
                'is_verified': True
            },
            {
                'title': 'Node.js - The Complete Guide',
                'url': 'https://www.udemy.com/course/nodejs-the-complete-guide/',
                'platform': 'udemy',
                'description': 'Master Node.js and build REST APIs',
                'topics': ['nodejs', 'javascript', 'backend', 'api'],
                'difficulty': 'intermediate',
                'rating': 4.7,
                'duration_hours': 40,
                'price': 0.0,
                'instructor': 'Maximilian Schwarzmüller',
                'is_verified': True
            },
            {
                'title': 'Complete Web Development Bootcamp',
                'url': 'https://www.udemy.com/course/the-complete-web-development-bootcamp/',
                'platform': 'udemy',
                'description': 'The only course you need to learn web development',
                'topics': ['web development', 'html', 'css', 'javascript', 'full stack'],
                'difficulty': 'beginner',
                'rating': 4.7,
                'duration_hours': 65,
                'price': 0.0,
                'instructor': 'Angela Yu',
                'is_verified': True
            },
            # Python
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
                'title': '100 Days of Code: The Complete Python Pro Bootcamp',
                'url': 'https://www.udemy.com/course/100-days-of-code/',
                'platform': 'udemy',
                'description': 'Master Python by building 100 projects',
                'topics': ['python', 'programming', 'projects'],
                'difficulty': 'beginner',
                'rating': 4.7,
                'duration_hours': 64,
                'price': 0.0,
                'instructor': 'Angela Yu',
                'is_verified': True
            },
            {
                'title': 'Python for Data Science and Machine Learning Bootcamp',
                'url': 'https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/',
                'platform': 'udemy',
                'description': 'Learn how to use NumPy, Pandas, Seaborn, Matplotlib, Plotly, Scikit-Learn, Machine Learning, Tensorflow, and more!',
                'topics': ['python', 'data science', 'machine learning', 'pandas', 'numpy'],
                'difficulty': 'intermediate',
                'rating': 4.6,
                'duration_hours': 25,
                'price': 0.0,
                'instructor': 'Jose Portilla',
                'is_verified': True
            },
            {
                'title': 'The Complete Python Bootcamp',
                'url': 'https://www.udemy.com/course/complete-python-bootcamp/',
                'platform': 'udemy',
                'description': 'Go from zero to hero in Python',
                'topics': ['python', 'programming'],
                'difficulty': 'beginner',
                'rating': 4.6,
                'duration_hours': 22,
                'price': 0.0,
                'instructor': 'Jose Portilla',
                'is_verified': True
            },
            # Machine Learning & AI
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
                'title': 'Deep Learning Specialization',
                'url': 'https://www.coursera.org/specializations/deep-learning',
                'platform': 'coursera',
                'description': 'Build Neural Networks and Deep Learning',
                'topics': ['deep learning', 'neural networks', 'ai', 'tensorflow'],
                'difficulty': 'intermediate',
                'rating': 4.9,
                'duration_hours': 120,
                'price': 0.0,
                'instructor': 'Andrew Ng',
                'is_verified': True
            },
            {
                'title': 'TensorFlow Developer Certificate',
                'url': 'https://www.coursera.org/professional-certificates/tensorflow-in-practice',
                'platform': 'coursera',
                'description': 'Build and train neural network models',
                'topics': ['tensorflow', 'deep learning', 'neural networks'],
                'difficulty': 'intermediate',
                'rating': 4.7,
                'duration_hours': 80,
                'price': 0.0,
                'instructor': 'Laurence Moroney',
                'is_verified': True
            },
            # Data Science
            {
                'title': 'Data Science Specialization',
                'url': 'https://www.coursera.org/specializations/jhu-data-science',
                'platform': 'coursera',
                'description': 'Learn Data Science from Johns Hopkins',
                'topics': ['data science', 'r', 'statistics', 'machine learning'],
                'difficulty': 'intermediate',
                'rating': 4.5,
                'duration_hours': 200,
                'price': 0.0,
                'instructor': 'Jeff Leek, Roger Peng, Brian Caffo',
                'is_verified': True
            },
            {
                'title': 'Data Science and Machine Learning Bootcamp',
                'url': 'https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/',
                'platform': 'udemy',
                'description': 'Complete Data Science and Machine Learning Bootcamp',
                'topics': ['data science', 'machine learning', 'python', 'pandas'],
                'difficulty': 'intermediate',
                'rating': 4.6,
                'duration_hours': 25,
                'price': 0.0,
                'instructor': 'Jose Portilla',
                'is_verified': True
            },
            # Backend & DevOps
            {
                'title': 'Docker & Kubernetes: The Practical Guide',
                'url': 'https://www.udemy.com/course/docker-kubernetes-the-practical-guide/',
                'platform': 'udemy',
                'description': 'Learn Docker, Kubernetes, and containerization',
                'topics': ['docker', 'kubernetes', 'devops', 'containers'],
                'difficulty': 'intermediate',
                'rating': 4.7,
                'duration_hours': 25,
                'price': 0.0,
                'instructor': 'Maximilian Schwarzmüller',
                'is_verified': True
            },
            {
                'title': 'AWS Certified Solutions Architect',
                'url': 'https://www.udemy.com/course/aws-certified-solutions-architect-associate/',
                'platform': 'udemy',
                'description': 'AWS Solutions Architect Associate Certification',
                'topics': ['aws', 'cloud', 'devops', 'architecture'],
                'difficulty': 'intermediate',
                'rating': 4.6,
                'duration_hours': 27,
                'price': 0.0,
                'instructor': 'Ryan Kroonenburg',
                'is_verified': True
            },
            {
                'title': 'The Complete SQL Bootcamp',
                'url': 'https://www.udemy.com/course/the-complete-sql-bootcamp/',
                'platform': 'udemy',
                'description': 'Go from zero to hero in SQL',
                'topics': ['sql', 'database', 'postgresql'],
                'difficulty': 'beginner',
                'rating': 4.7,
                'duration_hours': 9,
                'price': 0.0,
                'instructor': 'Jose Portilla',
                'is_verified': True
            },
            # Mobile Development
            {
                'title': 'iOS & Swift - The Complete iOS App Development Bootcamp',
                'url': 'https://www.udemy.com/course/ios-13-app-development-bootcamp/',
                'platform': 'udemy',
                'description': 'From Beginner to iOS App Developer',
                'topics': ['ios', 'swift', 'mobile development'],
                'difficulty': 'beginner',
                'rating': 4.8,
                'duration_hours': 60,
                'price': 0.0,
                'instructor': 'Angela Yu',
                'is_verified': True
            },
            {
                'title': 'The Complete Android Development Bootcamp',
                'url': 'https://www.udemy.com/course/complete-android-kotlin-developer-course/',
                'platform': 'udemy',
                'description': 'Learn Android App Development with Kotlin',
                'topics': ['android', 'kotlin', 'mobile development'],
                'difficulty': 'beginner',
                'rating': 4.6,
                'duration_hours': 50,
                'price': 0.0,
                'instructor': 'Denis Panjuta',
                'is_verified': True
            },
            {
                'title': 'React Native - The Practical Guide',
                'url': 'https://www.udemy.com/course/react-native-the-practical-guide/',
                'platform': 'udemy',
                'description': 'Build native mobile apps with React Native',
                'topics': ['react native', 'mobile development', 'javascript'],
                'difficulty': 'intermediate',
                'rating': 4.6,
                'duration_hours': 30,
                'price': 0.0,
                'instructor': 'Maximilian Schwarzmüller',
                'is_verified': True
            },
            # Free Platforms
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
            {
                'title': 'Khan Academy - Computer Programming',
                'url': 'https://www.khanacademy.org/computing/computer-programming',
                'platform': 'khanacademy',
                'description': 'Learn programming fundamentals',
                'topics': ['programming', 'javascript', 'html', 'css'],
                'difficulty': 'beginner',
                'rating': 4.7,
                'duration_hours': 50,
                'price': 0.0,
                'instructor': 'Khan Academy',
                'is_verified': True
            },
            {
                'title': 'Codecademy - Learn to Code',
                'url': 'https://www.codecademy.com/learn',
                'platform': 'codecademy',
                'description': 'Interactive coding lessons',
                'topics': ['programming', 'web development', 'python', 'javascript'],
                'difficulty': 'beginner',
                'rating': 4.5,
                'duration_hours': 100,
                'price': 0.0,
                'instructor': 'Codecademy',
                'is_verified': True
            },
            # YouTube Channels (Popular Programming Channels)
            {
                'title': 'Traversy Media - Web Development Tutorials',
                'url': 'https://www.youtube.com/c/TraversyMedia',
                'platform': 'youtube',
                'description': 'Web development tutorials and courses',
                'topics': ['web development', 'javascript', 'react', 'nodejs'],
                'difficulty': 'beginner',
                'rating': 4.8,
                'duration_hours': 200,
                'price': 0.0,
                'instructor': 'Brad Traversy',
                'is_verified': True
            },
            {
                'title': 'freeCodeCamp.org - Full Courses',
                'url': 'https://www.youtube.com/c/Freecodecamp',
                'platform': 'youtube',
                'description': 'Full programming courses for free',
                'topics': ['programming', 'web development', 'python', 'javascript'],
                'difficulty': 'beginner',
                'rating': 4.9,
                'duration_hours': 500,
                'price': 0.0,
                'instructor': 'freeCodeCamp',
                'is_verified': True
            },
            {
                'title': 'The Net Ninja - Programming Tutorials',
                'url': 'https://www.youtube.com/c/TheNetNinja',
                'platform': 'youtube',
                'description': 'Modern web development tutorials',
                'topics': ['web development', 'react', 'vue', 'nodejs'],
                'difficulty': 'beginner',
                'rating': 4.7,
                'duration_hours': 150,
                'price': 0.0,
                'instructor': 'Shaun Pelling',
                'is_verified': True
            },
            {
                'title': 'Programming with Mosh - Python, JavaScript, etc.',
                'url': 'https://www.youtube.com/c/programmingwithmosh',
                'platform': 'youtube',
                'description': 'Programming tutorials for beginners',
                'topics': ['python', 'javascript', 'programming'],
                'difficulty': 'beginner',
                'rating': 4.8,
                'duration_hours': 100,
                'price': 0.0,
                'instructor': 'Mosh Hamedani',
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

