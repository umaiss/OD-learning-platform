from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import settings

# Import existing routers
from routes import skill_profile, learning_path, content, missions, chatbot, progress

# Import new routers
from routers import (
    profile_router,
    learning_path_router,
    content_router,
    missions_router,
    progress_router,
    chatbot_router
)

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

# Include existing routers
app.include_router(skill_profile.router, prefix=settings.api_v1_prefix)
app.include_router(learning_path.router, prefix=settings.api_v1_prefix)
app.include_router(content.router, prefix=settings.api_v1_prefix)
app.include_router(missions.router, prefix=settings.api_v1_prefix)
app.include_router(chatbot.router, prefix=settings.api_v1_prefix)
app.include_router(progress.router, prefix=settings.api_v1_prefix)

# Include new routers
app.include_router(profile_router, prefix=settings.api_v1_prefix)
app.include_router(learning_path_router, prefix=settings.api_v1_prefix)
app.include_router(content_router, prefix=settings.api_v1_prefix)
app.include_router(missions_router, prefix=settings.api_v1_prefix)
app.include_router(progress_router, prefix=settings.api_v1_prefix)
app.include_router(chatbot_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return JSONResponse(
        content={
            "message": "Learning Platform API is running",
            "status": "healthy",
            "version": "1.0.0"
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

