"""
Test script for scraping specific course URLs
Usage: python scrapers/test_scraper.py "url1" "url2" "url3"
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


async def test_scrape_url(url: str, topics: list = None, difficulty: str = "intermediate"):
    """Test scraping a single URL"""
    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print(f"{'='*60}")
    
    db = next(get_db())
    scraper = CourseScraper(db)
    
    try:
        # Try to scrape
        print(f"\n1. Attempting to scrape...")
        course = scraper.add_course_from_url(url, topics=topics, difficulty=difficulty)
        
        if course:
            print(f"   ✓ Successfully scraped!")
            print(f"\n   Course Details:")
            print(f"   - Title: {course.title}")
            print(f"   - Platform: {course.platform}")
            print(f"   - Instructor: {course.instructor}")
            print(f"   - Description: {course.description[:100]}..." if course.description else "   - Description: (none)")
            print(f"   - Rating: {course.rating}")
            print(f"   - Topics: {', '.join(course.topics or [])}")
            print(f"   - Difficulty: {course.difficulty}")
            print(f"   - Is Free: {course.is_free}")
            print(f"   - Is Verified: {course.is_verified}")
            
            # Create embedding
            print(f"\n2. Creating vector embedding...")
            try:
                course_text = f"{course.title} {course.description or ''} {' '.join(course.topics or [])}"
                await create_embeddings_for_content(
                    db=db,
                    text=course_text,
                    content_type="course",
                    course_id=course.id
                )
                print(f"   ✓ Embedding created successfully")
            except Exception as e:
                print(f"   ⚠ Failed to create embedding: {str(e)}")
            
            print(f"\n   ✓ Course ID: {course.id}")
            return True
        else:
            print(f"   ✗ Failed to scrape (may be due to anti-scraping measures)")
            print(f"\n   Possible reasons:")
            print(f"   - Platform requires login/authentication")
            print(f"   - Anti-scraping measures (CAPTCHA, rate limiting)")
            print(f"   - URL structure changed")
            print(f"   - Network/connection issues")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        import traceback
        print(f"\n   Full error:")
        traceback.print_exc()
        return False
    finally:
        db.close()


async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python scrapers/test_scraper.py <url1> [url2] [url3] ...")
        print("\nExample:")
        print('  python scrapers/test_scraper.py "https://www.udemy.com/course/react-the-complete-guide/"')
        print('  python scrapers/test_scraper.py "https://www.youtube.com/watch?v=example" "https://www.coursera.org/learn/example"')
        print("\nOr test with default URLs:")
        test_urls = [
            "https://www.youtube.com/watch?v=8aGhZQkoFbQ",  # Should work (YouTube oEmbed)
            "https://www.udemy.com/course/react-the-complete-guide-incl-redux/",  # May work
            "https://www.coursera.org/learn/machine-learning",  # May work
        ]
        print("\nTesting with default URLs...")
        for url in test_urls:
            await test_scrape_url(url)
            await asyncio.sleep(1)  # Rate limiting
        return
    
    # Get URLs from command line
    urls = sys.argv[1:]
    
    print(f"Testing {len(urls)} URL(s)...")
    print("Note: Some platforms have anti-scraping measures, so some may fail.\n")
    
    results = {"success": 0, "failed": 0}
    
    for url in urls:
        # Auto-detect topics from URL
        topics = []
        difficulty = "intermediate"
        
        url_lower = url.lower()
        if 'javascript' in url_lower or 'js' in url_lower:
            topics = ['javascript', 'web development']
        elif 'react' in url_lower:
            topics = ['react', 'javascript', 'frontend']
        elif 'python' in url_lower:
            topics = ['python', 'programming']
        elif 'machine-learning' in url_lower or 'ml' in url_lower:
            topics = ['machine learning', 'ai', 'data science']
        elif 'node' in url_lower:
            topics = ['nodejs', 'javascript', 'backend']
        elif 'vue' in url_lower:
            topics = ['vuejs', 'javascript', 'frontend']
        elif 'angular' in url_lower:
            topics = ['angular', 'typescript', 'frontend']
        
        success = await test_scrape_url(url, topics=topics, difficulty=difficulty)
        
        if success:
            results["success"] += 1
        else:
            results["failed"] += 1
        
        # Rate limiting between requests
        if url != urls[-1]:  # Don't sleep after last URL
            await asyncio.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Successful: {results['success']}")
    print(f"  Failed: {results['failed']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())

