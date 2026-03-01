from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
from datetime import datetime

from api import interview_routes, user_routes, leaderboard_routes
from database.database import engine, Base
from config.settings import settings

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="AI Interview Simulator",
    description="A comprehensive platform for conducting AI-powered technical interviews",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(interview_routes.router, prefix="/api/v1/interview", tags=["interview"])
app.include_router(user_routes.router, prefix="/api/v1/user", tags=["user"])
app.include_router(leaderboard_routes.router, prefix="/api/v1/leaderboard", tags=["leaderboard"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Interview Simulator API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )