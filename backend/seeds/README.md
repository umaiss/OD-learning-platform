# Database Seeding

This directory contains scripts to seed the database with demo data for testing and development.

## Seed Data Script

The `seed_data.py` script creates:
- 1 demo learner with sample data
- Sample skill map (10 skills with different levels)
- Sample progress record (completed modules, XP, streak)

## Usage

### Prerequisites

1. Make sure the database is initialized:
   ```bash
   python db/init_db.py
   ```

2. Ensure your `.env` file has the correct database connection settings.

### Running the Seed Script

From the `backend` directory:

```bash
python seeds/seed_data.py
```

Or using the virtual environment:

```bash
source venv/bin/activate
python seeds/seed_data.py
```

## Demo Learner Data

The seed script creates a demo learner with:

- **Name**: Demo Learner
- **Role**: software engineer
- **Experience**: 3 years
- **Skill Map**: 10 skills (Python, JavaScript, React, Docker, Kubernetes, PostgreSQL, FastAPI, TypeScript, AWS, CI/CD)
- **Progress**: 
  - 4 completed modules
  - 250 XP points
  - 7-day learning streak

## Notes

- The script is idempotent - running it multiple times will update existing records instead of creating duplicates
- The demo learner is identified by name "Demo Learner"
- Progress records are linked to the learner by ID

## Using the Demo Data

After seeding, you can use the demo learner ID to test API endpoints:

```bash
# Example: Get the learner ID from the output
# Then use it in API calls:
curl -X POST http://localhost:8000/api/v1/profile/generate \
  -H "Content-Type: application/json" \
  -d '{
    "learner_id": 1,
    "self_assessment": "...",
    "role": "software engineer",
    "experience": 3
  }'
```

