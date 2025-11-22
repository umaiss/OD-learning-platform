"""
Script to scrape courses from a list of URLs
This attempts to fetch course data from actual URLs
Note: Many platforms have anti-scraping measures, so this may not work for all URLs
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


async def scrape_courses_from_urls(urls_file: str = None):
    """
    Scrape courses from a list of URLs
    
    Args:
        urls_file: Optional path to a file containing URLs (one per line)
    """
    print("Starting course scraping from URLs...")
    
    # Get database session
    db = next(get_db())
    scraper = CourseScraper(db)
    
    # Default list of URLs to try scraping
    default_urls = [
        # Udemy courses (may fail due to anti-scraping)
        'https://www.udemy.com/course/the-complete-javascript-course/',
        'https://www.udemy.com/course/react-the-complete-guide-incl-redux/',
        'https://www.udemy.com/course/nodejs-the-complete-guide/',
        'https://www.udemy.com/course/the-complete-web-development-bootcamp/',
        # Coursera courses
        'https://www.coursera.org/learn/machine-learning',
        'https://www.coursera.org/specializations/python',
        # YouTube videos
        'https://www.youtube.com/watch?v=8aGhZQkoFbQ',  # Event Loop
        'https://www.youtube.com/watch?v=DLX62G4lc44',  # React Tutorial
    ]
    
    # If URLs file provided, read from file
    urls_to_scrape = default_urls
    if urls_file:
        try:
            with open(urls_file, 'r') as f:
                urls_to_scrape = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Error reading URLs file: {e}")
            print("Using default URLs...")
    
    print(f"\nAttempting to scrape {len(urls_to_scrape)} URLs...")
    print("Note: Many platforms have anti-scraping measures, so some may fail.\n")
    
    successful = 0
    failed = 0
    
    for url in urls_to_scrape:
        try:
            print(f"Scraping: {url}")
            
            # Detect platform and extract topics/difficulty from URL if possible
            topics = []
            difficulty = "intermediate"
            
            if 'javascript' in url.lower() or 'js' in url.lower():
                topics = ['javascript', 'web development']
            elif 'react' in url.lower():
                topics = ['react', 'javascript', 'frontend']
            elif 'python' in url.lower():
                topics = ['python', 'programming']
            elif 'machine-learning' in url.lower() or 'ml' in url.lower():
                topics = ['machine learning', 'ai', 'data science']
            
            # Try to scrape
            course = scraper.add_course_from_url(url, topics=topics, difficulty=difficulty)
            
            if course:
                print(f"  ✓ Successfully added: {course.title}")
                successful += 1
                
                # Create embedding
                try:
                    course_text = f"{course.title} {course.description or ''} {' '.join(course.topics or [])}"
                    await create_embeddings_for_content(
                        db=db,
                        text=course_text,
                        content_type="course",
                        course_id=course.id
                    )
                    print(f"    ✓ Created embedding")
                except Exception as e:
                    print(f"    ⚠ Failed to create embedding: {str(e)}")
            else:
                print(f"  ✗ Failed to scrape (may be due to anti-scraping measures)")
                failed += 1
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            failed += 1
        
        # Rate limiting - be respectful
        await asyncio.sleep(2)
    
    print(f"\n✓ Scraping complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"\nNote: If many failed, it's likely due to anti-scraping measures.")
    print("Consider using the manual seed list or official APIs.")
    
    db.close()


if __name__ == "__main__":
    import sys
    urls_file = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(scrape_courses_from_urls(urls_file))

