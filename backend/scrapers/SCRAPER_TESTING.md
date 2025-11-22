# Course Scraper Testing Guide

## Quick Test

Test the scraper with specific URLs:

```bash
# Test a single URL
python scrapers/test_scraper.py "https://www.youtube.com/watch?v=8aGhZQkoFbQ"

# Test multiple URLs
python scrapers/test_scraper.py \
  "https://www.udemy.com/course/react-the-complete-guide-incl-redux/" \
  "https://www.coursera.org/learn/machine-learning" \
  "https://www.youtube.com/watch?v=DLX62G4lc44"
```

## What Gets Tested

1. **URL Scraping** - Attempts to fetch course data from the URL
2. **Data Extraction** - Extracts title, description, instructor, rating, etc.
3. **Database Storage** - Saves course to database
4. **Vector Embedding** - Creates embedding for semantic search

## Expected Results by Platform

### YouTube ✅ (Usually Works)
- Uses oEmbed API (no authentication needed)
- Success rate: ~90%
- Example: `https://www.youtube.com/watch?v=8aGhZQkoFbQ`

### Udemy ⚠️ (May Fail)
- Has anti-scraping measures
- May require login
- Success rate: ~30-50%
- Example: `https://www.udemy.com/course/react-the-complete-guide-incl-redux/`

### Coursera ⚠️ (May Fail)
- Has anti-scraping measures
- May require login
- Success rate: ~30-50%
- Example: `https://www.coursera.org/learn/machine-learning`

## Testing Workflow

1. **Test with YouTube first** (most reliable):
   ```bash
   python scrapers/test_scraper.py "https://www.youtube.com/watch?v=8aGhZQkoFbQ"
   ```

2. **Test with Udemy/Coursera** (may fail):
   ```bash
   python scrapers/test_scraper.py "https://www.udemy.com/course/example/"
   ```

3. **Check results in database**:
   ```bash
   python -c "from db.database import get_db; from db.models import Course; db = next(get_db()); courses = db.query(Course).all(); print(f'Total: {len(courses)} courses'); [print(f'- {c.title} ({c.platform})') for c in courses[-5:]]"
   ```

## Troubleshooting

### "Failed to scrape" Errors

**Common causes:**
1. **Anti-scraping measures** - Platform blocks automated requests
2. **Login required** - Course page requires authentication
3. **URL structure changed** - Platform updated their HTML
4. **Rate limiting** - Too many requests too quickly

**Solutions:**
- Use manual seed list for reliable courses
- Use official APIs where available
- Add delays between requests
- Use Selenium/Playwright for JavaScript-rendered pages

### "Network error" Errors

**Common causes:**
1. No internet connection
2. Firewall blocking requests
3. DNS issues
4. Platform is down

**Solutions:**
- Check internet connection
- Try a different URL
- Wait and retry later

## Best Practices

1. **Start with YouTube** - Most reliable platform
2. **Use seed list for verified courses** - More reliable than scraping
3. **Test URLs individually** - Easier to debug
4. **Add delays** - Respect rate limits (2+ seconds between requests)
5. **Verify results** - Check database after scraping

## Example Test Session

```bash
# 1. Test YouTube (should work)
$ python scrapers/test_scraper.py "https://www.youtube.com/watch?v=8aGhZQkoFbQ"
✓ Successfully scraped!

# 2. Test Udemy (may work)
$ python scrapers/test_scraper.py "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"
⚠ Redirected to login page (anti-scraping measure)
✗ Failed to scrape

# 3. Check what was added
$ python -c "from db.database import get_db; from db.models import Course; db = next(get_db()); print(f'Total courses: {db.query(Course).count()}')"
Total courses: 30
```

## Adding More Test URLs

Create a file `test_urls.txt`:
```
https://www.youtube.com/watch?v=example1
https://www.udemy.com/course/example2/
https://www.coursera.org/learn/example3
```

Then use:
```bash
python scrapers/scrape_courses_from_urls.py test_urls.txt
```

