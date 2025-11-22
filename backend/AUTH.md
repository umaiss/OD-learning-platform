# Authentication System

Complete authentication system for Learner, Manager, and Mentor roles.

## Features

- ✅ Manager signup (only managers can sign up publicly)
- ✅ Manager creates users for Learners and Mentors
- ✅ User login with JWT tokens
- ✅ Password hashing with bcrypt
- ✅ Role-based access control
- ✅ User-Learner relationship (one-to-one)
- ✅ Protected endpoints with authentication

## Database Changes

### User Model
- Added `password_hash` field (hashed passwords)
- Added `role` field (learner, manager, mentor)
- Added `is_active` field (account status)
- Added relationship to `Learner` model

### Learner Model
- Added `user_id` foreign key (one-to-one relationship with User)
- Renamed `role` to `professional_role` (to avoid confusion with user role)
- Added relationship back to `User` model

## API Endpoints

### Signup (Manager Only)
```bash
POST /api/v1/auth/signup
Content-Type: application/json

{
  "email": "manager@example.com",
  "password": "securepassword123",
  "name": "Manager Name",
  "role": "manager"  # Only "manager" is allowed for public signup
}
```

**Response:**
```json
{
  "id": 1,
  "email": "manager@example.com",
  "name": "Manager Name",
  "role": "manager",
  "message": "User created successfully"
}
```

**Note**: Only managers can sign up. Learners and Mentors must be created by managers.

### Create User (Manager Only)
```bash
POST /api/v1/auth/create-user
Authorization: Bearer <manager_token>
Content-Type: application/json

{
  "email": "learner@example.com",
  "password": "securepassword123",
  "name": "Learner Name",
  "role": "learner",  # or "mentor"
  "professional_role": "developer",  # Optional, for learners
  "experience_years": 3  # Optional, for learners
}
```

**Response:**
```json
{
  "id": 2,
  "email": "learner@example.com",
  "name": "Learner Name",
  "role": "learner",
  "message": "User created successfully"
}
```

**Note**: This endpoint requires manager authentication. Only managers can create learners and mentors.

### Login (OAuth2 Form)
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com
password=securepassword123
```

### Login (JSON)
```bash
POST /api/v1/auth/login-json
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "learner"
  }
}
```

### Get Current User
```bash
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "learner",
  "is_active": true
}
```

## Using Authentication in Routes

### Protect an endpoint (any authenticated user)
```python
from core.dependencies import get_current_user
from db.models import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.name}"}
```

### Require specific role
```python
from core.dependencies import require_role

@router.get("/learner-only")
async def learner_route(
    current_user: User = Depends(require_role(["learner"]))
):
    return {"message": "Learner access granted"}
```

### Get learner profile for authenticated user
```python
from core.dependencies import get_current_learner
from db.models import Learner

@router.get("/my-profile")
async def my_profile(learner: Learner = Depends(get_current_learner)):
    return {
        "learner_id": learner.id,
        "professional_role": learner.professional_role,
        "skill_map": learner.skill_map
    }
```

## Environment Variables

Add to `.env`:
```env
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=43200  # 30 days
```

## Installation

Install new dependencies:
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart email-validator
```

Or reinstall all:
```bash
pip install -r requirements.txt
```

## Database Migration

After updating models, you need to recreate the database:

```bash
# Drop and recreate tables (WARNING: This deletes all data)
python db/init_db.py
```

Or use Alembic for migrations (recommended for production):
```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add authentication"

# Apply migration
alembic upgrade head
```

## Example Usage

### Signup as Manager (Public)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@example.com",
    "password": "password123",
    "name": "Manager Name",
    "role": "manager"
  }'
```

### Manager Creates Learner
```bash
# First, manager logs in to get token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"email": "manager@example.com", "password": "password123"}' \
  | jq -r '.access_token')

# Then create learner
curl -X POST "http://localhost:8000/api/v1/auth/create-user" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "email": "learner@example.com",
    "password": "password123",
    "name": "Jane Learner",
    "role": "learner",
    "professional_role": "developer",
    "experience_years": 2
  }'
```

### Manager Creates Mentor
```bash
curl -X POST "http://localhost:8000/api/v1/auth/create-user" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "email": "mentor@example.com",
    "password": "password123",
    "name": "John Mentor",
    "role": "mentor"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "learner@example.com",
    "password": "password123"
  }'
```

### Use Token
```bash
TOKEN="your-access-token-here"

curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

## Security Notes

1. **JWT Secret Key**: Change `JWT_SECRET_KEY` in production
2. **Password Strength**: Consider adding password validation
3. **Token Expiration**: Default is 30 days, adjust as needed
4. **HTTPS**: Always use HTTPS in production
5. **Rate Limiting**: Consider adding rate limiting for login endpoints

## Next Steps

- Update existing routes to use authentication
- Add password reset functionality
- Add email verification
- Add refresh tokens
- Add role-specific endpoints for managers and mentors

