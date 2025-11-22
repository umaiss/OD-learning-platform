# Course Suggestion System - Hybrid Approach

## Overview

The platform uses a **hybrid approach** for course suggestions, combining:
1. **Local Database** - Curated, verified courses with vector embeddings
2. **LLM Suggestions** - AI-generated personalized course recommendations
3. **Manual Addition** - Users can add custom courses

## Architecture

### Components

1. **Course Model** (`db/models.py`)
   - Stores course information (title, URL, platform, topics, difficulty, etc.)
   - Supports vector embeddings for semantic search

2. **Course Scraper** (`scrapers/course_scraper.py`)
   - Scrapes course data from Udemy, Coursera, YouTube
   - Manual course addition for curated content
   - Note: Respects robots.txt and rate limits

3. **Course Suggester Agent** (`agents/course_suggester.py`)
   - Searches local database using vector similarity
   - Falls back to LLM suggestions if needed
   - Combines and ranks results

4. **Vector Embeddings**
   - Each course has an embedding for semantic search
   - Enables finding relevant courses based on module content

## Setup

### 1. Initialize Database

```bash
# Create tables (including courses table)
python db/init_db.py
```

### 2. Seed Course Database

```bash
# Seed with popular courses and create embeddings
python scrapers/seed_courses.py
```

This will:
- Add 5+ popular courses (JavaScript, React, Python, ML, etc.)
- Create vector embeddings for semantic search
- Mark courses as verified

### 3. Add More Courses

**Option A: Via API (Manager only)**
```bash
POST /api/v1/courses/add
{
  "url": "https://www.udemy.com/course/example",
  "topics": ["react", "javascript"],
  "difficulty": "intermediate"
}
```

**Option B: Manual Entry**
Edit `scrapers/seed_courses.py` and add more courses to the `popular_courses` list.

## How It Works

### Auto-Suggestion Flow

1. **Learning Path Generated** → Modules created
2. **For Each Module**:
   - System searches local database using vector similarity
   - Finds courses matching module name/description
   - If not enough results, LLM suggests additional courses
   - Combines results and removes duplicates
3. **Suggestions Added** → Stored in learning plan JSON
4. **Frontend Displays** → User can accept/reject/modify

### Search Strategy

1. **Vector Search** (Primary):
   - Generates embedding for module query
   - Searches course embeddings using cosine similarity
   - Returns top matches above similarity threshold (0.3)

2. **Text Search** (Fallback):
   - If vector search fails, uses text-based search
   - Searches in title, description, and topics
   - Scores by relevance

3. **LLM Suggestions** (Supplement):
   - If not enough results from database
   - LLM generates course suggestions based on module content
   - Note: These may need validation (URLs might not exist)

## API Endpoints

### Suggest Courses
```http
POST /api/v1/courses/suggest
{
  "learner_id": 1,
  "module_name": "React Fundamentals",
  "module_description": "Introduction to React components",
  "skill_level": "intermediate",
  "limit": 5
}
```

### Add Course
```http
POST /api/v1/courses/add
{
  "url": "https://www.udemy.com/course/example",
  "topics": ["react", "javascript"],
  "difficulty": "intermediate"
}
```

### Search Courses
```http
GET /api/v1/courses/search?query=react&platform=udemy&difficulty=intermediate&limit=10
```

## Integration with Learning Path

When a learning path is generated (`/api/v1/learning-path/generate`):
- **Automatically suggests courses** for each module
- Stores suggestions in `learning_materials` field of each module
- Frontend can display these immediately

Example module structure:
```json
{
  "name": "React Fundamentals",
  "description": "Introduction to React components",
  "learning_materials": [
    {
      "title": "React - The Complete Guide",
      "url": "https://www.udemy.com/course/react-the-complete-guide/",
      "platform": "udemy",
      "type": "course",
      "estimated_hours": 50,
      "description": "Dive in and learn React from scratch"
    }
  ]
}
```

## Current Status

✅ **30 courses** in database (manually curated via seed script)
✅ **Vector embeddings** created for all courses
✅ **Scraper methods** implemented (but may fail due to anti-scraping)

## Expanding the Course Database

### Method 1: Seed Script (Recommended)
Edit `scrapers/seed_courses.py` and add more courses to the `popular_courses` list.
Currently has 30 courses - easy to expand to 100+.

### Method 2: API Endpoint
Use `/api/v1/courses/add` to add courses programmatically.

### Method 3: Scraper
Use `CourseScraper.add_course_from_url()` to scrape from URLs.

## Best Practices

1. **Verify Courses**: Mark manually added courses as `is_verified: true`
2. **Add Topics**: Include relevant topics for better search
3. **Set Difficulty**: Helps filter suggestions by skill level
4. **Regular Updates**: Periodically update course database
5. **Monitor LLM Suggestions**: Validate LLM-suggested URLs

## Future Enhancements

- [ ] Integration with official APIs (Udemy API, Coursera API)
- [ ] Course rating aggregation
- [ ] User reviews and ratings
- [ ] Course completion tracking
- [ ] Personalized recommendations based on user progress
- [ ] Course price tracking and alerts

