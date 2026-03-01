import subprocess
import sys
import os
from pathlib import Path


def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Requirements installed successfully!")


def setup_database():
    """Initialize the database"""
    print("Setting up database...")
    
    # Import all models to ensure they're registered with SQLAlchemy
    from models.user import User
    from models.interview import InterviewSession, InterviewQuestion, InterviewResponse
    from models.dsa_questions import DSAQuestion
    
    # Import and create tables
    from database.database import engine, Base
    Base.metadata.create_all(bind=engine)
    
    # Load sample questions
    from sqlalchemy.orm import Session
    from database.database import SessionLocal
    from utils.question_loader import load_sample_questions
    
    db = SessionLocal()
    try:
        load_sample_questions(db)
    finally:
        db.close()
    
    print("Database setup completed!")


def run_server():
    """Run the FastAPI server"""
    print("Starting the AI Interview Simulator server...")
    print("Access the application at: http://localhost:8000")
    print("API Documentation available at: http://localhost:8000/docs")
    
    import uvicorn
    from main import app
    from config.settings import settings
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )


def main():
    """Main setup function"""
    print("AI Interview Simulator Setup")
    print("="*40)
    
    # Change to the project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Install requirements
    install_requirements()
    
    # Setup database
    setup_database()
    
    # Run the server
    run_server()


if __name__ == "__main__":
    main()