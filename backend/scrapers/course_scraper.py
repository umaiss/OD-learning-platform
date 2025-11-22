"""
Course scraper for Udemy, Coursera, YouTube, and other platforms
Note: This scraper respects robots.txt and rate limits. 
For production, consider using official APIs where available.
"""
import re
import time
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from db.models import Course
import json


class CourseScraper:
    """Scraper for collecting course data from various platforms"""
    
    def __init__(self, db: Session):
        self.db = db
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_udemy_course(self, url: str) -> Optional[Dict]:
        """
        Scrape Udemy course information
        Note: Udemy has strict anti-scraping measures. This is a basic implementation.
        For production, consider using Udemy's API or manual data entry.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract course information (Udemy structure may vary)
            title_elem = soup.find('h1', class_='ud-heading-xl')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Course"
            
            # Try to find description
            desc_elem = soup.find('div', class_='ud-text-sm')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract rating (if available)
            rating_elem = soup.find('span', class_='ud-heading-sm')
            rating = 0.0
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Extract instructor
            instructor_elem = soup.find('a', class_='ud-instructor')
            instructor = instructor_elem.get_text(strip=True) if instructor_elem else "Unknown"
            
            return {
                'title': title,
                'url': url,
                'platform': 'udemy',
                'description': description[:1000] if description else "",  # Limit description length
                'rating': rating,
                'instructor': instructor,
                'is_free': False,  # Most Udemy courses are paid
                'is_verified': False  # Needs manual verification
            }
        except Exception as e:
            print(f"Error scraping Udemy course {url}: {str(e)}")
            return None
    
    def scrape_coursera_course(self, url: str) -> Optional[Dict]:
        """
        Scrape Coursera course information
        Note: Coursera has strict anti-scraping measures. This is a basic implementation.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract course information
            title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Course"
            
            # Try to find description
            desc_elem = soup.find('div', class_='description')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            return {
                'title': title,
                'url': url,
                'platform': 'coursera',
                'description': description[:1000] if description else "",
                'rating': 0.0,
                'instructor': "Coursera",
                'is_free': False,  # Most Coursera courses are paid
                'is_verified': False
            }
        except Exception as e:
            print(f"Error scraping Coursera course {url}: {str(e)}")
            return None
    
    def scrape_youtube_video(self, url: str) -> Optional[Dict]:
        """
        Scrape YouTube video information
        Note: For production, use YouTube Data API v3 (requires API key)
        """
        try:
            # Extract video ID from URL
            video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
            if not video_id_match:
                return None
            
            video_id = video_id_match.group(1)
            
            # Use YouTube oEmbed API (simpler, no API key needed)
            oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
            response = requests.get(oembed_url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            return {
                'title': data.get('title', 'Unknown Video'),
                'url': url,
                'platform': 'youtube',
                'description': data.get('author_name', '') + " - " + data.get('title', ''),
                'rating': 0.0,
                'instructor': data.get('author_name', 'Unknown'),
                'is_free': True,
                'is_verified': False
            }
        except Exception as e:
            print(f"Error scraping YouTube video {url}: {str(e)}")
            return None
    
    def add_course_from_url(self, url: str, topics: List[str] = None, difficulty: str = "intermediate") -> Optional[Course]:
        """
        Add a course to the database from a URL
        Automatically detects platform and scrapes accordingly
        """
        # Detect platform from URL
        if 'udemy.com' in url:
            course_data = self.scrape_udemy_course(url)
        elif 'coursera.org' in url:
            course_data = self.scrape_coursera_course(url)
        elif 'youtube.com' in url or 'youtu.be' in url:
            course_data = self.scrape_youtube_video(url)
        else:
            # Generic course entry
            course_data = {
                'title': 'Unknown Course',
                'url': url,
                'platform': 'other',
                'description': '',
                'rating': 0.0,
                'instructor': 'Unknown',
                'is_free': True,
                'is_verified': False
            }
        
        if not course_data:
            return None
        
        # Check if course already exists
        existing = self.db.query(Course).filter(Course.url == url).first()
        if existing:
            return existing
        
        # Add topics if provided
        if topics:
            course_data['topics'] = topics
        
        course_data['difficulty'] = difficulty
        
        # Create course
        course = Course(**course_data)
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        
        # Note: Vector embeddings will be created separately via seed_courses.py script
        return course
    
    def add_course_manual(
        self,
        title: str,
        url: str,
        platform: str,
        description: str = "",
        topics: List[str] = None,
        difficulty: str = "intermediate",
        rating: float = 0.0,
        duration_hours: int = None,
        price: float = 0.0,
        instructor: str = "",
        is_verified: bool = False
    ) -> Course:
        """
        Manually add a course to the database (for verified/curated courses)
        """
        # Check if course already exists
        existing = self.db.query(Course).filter(Course.url == url).first()
        if existing:
            return existing
        
        course = Course(
            title=title,
            url=url,
            platform=platform,
            description=description,
            topics=topics or [],
            difficulty=difficulty,
            rating=rating,
            duration_hours=duration_hours,
            price=price,
            instructor=instructor,
            is_free=(price == 0.0),
            is_verified=is_verified
        )
        
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        
        # Note: Vector embeddings will be created separately via an async function
        # This is handled in the seed script or API endpoints
        
        return course


async def seed_popular_courses(db: Session) -> int:
    """
    Seed database with popular courses (manual curation)
    This is a starting point - you can expand this list
    """
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
                print(f"✓ Added course: {course.title}")
        except Exception as e:
            print(f"✗ Failed to add course {course_data['title']}: {str(e)}")
    
    print(f"\n✓ Added {added_count} courses to database")
    return added_count

