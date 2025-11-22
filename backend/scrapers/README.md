# Course Scraper Documentation

## Overview

The course scraper has two approaches:
1. **Manual Seed List** - Curated list of 30+ popular courses (recommended)
2. **URL Scraping** - Attempts to scrape course data from URLs (may fail due to anti-scraping)

## Why Scraping Often Fails

Udemy, Coursera, and other platforms have strict anti-scraping measures:
- Require login/authentication
- Use JavaScript rendering (requires Selenium/Playwright)
- Rate limiting and IP blocking
- Dynamic HTML structure that changes frequently

## Recommended Approach

**Use the manual seed list** - It's more reliable and faster:
```bash
python scrapers/seed_courses.py
```

This adds 30+ verified courses with complete metadata.

## Trying to Scrape from URLs

If you want to attempt scraping (may have limited success):

### Option 1: Use the scraper script
```bash
# Create a file with URLs (one per line)
echo "https://www.udemy.com/course/example/" > urls.txt
echo "https://www.coursera.org/learn/example" >> urls.txt

# Run the scraper
python scrapers/scrape_courses_from_urls.py urls.txt
```

### Option 2: Use the API
```bash
POST /api/v1/courses/add
{
  "url": "https://www.udemy.com/course/example/",
  "topics": ["javascript", "react"],
  "difficulty": "intermediate"
}
```

## Current Status

✅ **30 courses added** via seed script (manually curated)
⚠️ **Scraping from URLs** - Limited success due to anti-scraping measures

## Expanding the Database

### Method 1: Add to Seed List (Recommended)
Edit `scrapers/seed_courses.py` and add more courses to the `popular_courses` list.

### Method 2: Use Official APIs
- **Udemy API**: Requires API key, limited access
- **Coursera API**: Limited public access
- **YouTube Data API**: Free, requires API key

### Method 3: Manual Entry via API
Use `/api/v1/courses/add` endpoint to add courses manually.

## Improving the Scraper

For better scraping results, consider:
1. Using Selenium/Playwright for JavaScript-rendered pages
2. Implementing login/authentication
3. Using official APIs where available
4. Adding delays and respecting rate limits
5. Using proxy rotation for large-scale scraping

