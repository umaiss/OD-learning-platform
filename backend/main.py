from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI(
    title="Learning Platform API",
    description="Backend API for the Learning Platform",
    version="1.0.0"
)

# Configure CORS to allow requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return JSONResponse(
        content={
            "message": "Learning Platform API is running",
            "status": "healthy"
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "learning-platform-api"
        }
    )


# Example endpoint - can be removed or modified
@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API connectivity"""
    return JSONResponse(
        content={
            "message": "API is working correctly",
            "data": {"test": True}
        }
    )

