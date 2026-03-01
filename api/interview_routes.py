from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database.database import get_db
from models.user import User
from models.interview import InterviewSession, InterviewResponse
from models.dsa_questions import DSAQuestion, DifficultyLevel
from schemas.interview import (
    InterviewSession as InterviewSessionSchema,
    InterviewSessionCreate,
    InterviewResponse as InterviewResponseSchema,
    InterviewResponseCreate
)
from schemas.dsa_questions import DSAQuestion as DSAQuestionSchema
from utils.database_utils import (
    get_user,
    get_interview_session,
    create_interview_session,
    get_dsa_questions_by_difficulty,
    create_interview_response,
    update_interview_response_score,
    get_user_interview_sessions,
    get_interview_responses
)
from sqlalchemy import and_
from models.dsa_questions import DSAQuestion
from utils.ai_evaluator import ai_evaluator
from utils.question_loader import load_sample_questions


router = APIRouter()


@router.post("/start", response_model=InterviewSessionSchema)
def start_interview(
    interview_data: InterviewSessionCreate,
    db: Session = Depends(get_db)
):
    """Start a new interview session"""
    # Verify user exists
    user = get_user(db, interview_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Load sample questions if not already loaded
    load_sample_questions(db)
    
    # Create interview session
    db_session = create_interview_session(
        db, 
        interview_data.user_id, 
        interview_data.interview_type
    )
    
    return db_session


@router.get("/{session_id}/questions", response_model=List[DSAQuestionSchema])
def get_interview_questions(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get questions for the interview session based on user level"""
    session = get_interview_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    user = get_user(db, session.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get questions based on user's level
    # Convert string level to enum
    level_enum = DifficultyLevel(user.level)
    questions = get_dsa_questions_by_difficulty(db, level_enum, limit=5)
    return questions


class InterviewResponseCreateWithCode(BaseModel):
    interview_session_id: int
    interview_question_id: int
    response_text: str
    programming_language: Optional[str] = None
    execution_time: Optional[float] = None

@router.post("/{session_id}/response", response_model=InterviewResponseSchema)
def submit_response(
    session_id: int,
    response_data: InterviewResponseCreateWithCode,
    db: Session = Depends(get_db)
):
    """Submit a response to an interview question"""
    session = get_interview_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    # Create the response record
    db_response = create_interview_response(
        db,
        response_data.interview_session_id,
        response_data.interview_question_id,
        response_data.response_text,
        response_data.programming_language,
        response_data.execution_time
    )
    
    # Get the question details to pass to evaluator
    question = db.query(DSAQuestion).filter(
        DSAQuestion.id == response_data.interview_question_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Evaluate the response using AI
    evaluation_result = ai_evaluator.evaluate_response(
        question.description,
        response_data.response_text,
        question.solution
    )
    
    # Update the response with evaluation scores
    updated_response = update_interview_response_score(
        db,
        db_response.id,
        evaluation_result["final_score"],
        evaluation_result["technical_accuracy"],
        evaluation_result["problem_solving_logic"],
        evaluation_result["communication_clarity"],
        evaluation_result["feedback"],
        evaluation_result["ai_evaluation"]
    )
    
    return updated_response


@router.get("/{session_id}", response_model=InterviewSessionSchema)
def get_interview_session_endpoint(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get details of an interview session"""
    session = get_interview_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    return session


@router.post("/{session_id}/complete")
def complete_interview(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Mark an interview session as completed"""
    session = get_interview_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    # Update session status to completed
    session.status = "completed"
    session.ended_at = func.now()
    db.commit()
    
    return {"message": "Interview session completed successfully", "session_id": session_id}


@router.get("/user/{user_id}/sessions")
def get_user_interview_sessions_endpoint(
    user_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get all interview sessions for a user"""
    # Verify user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    sessions = get_user_interview_sessions(db, user_id, limit)
    
    # Convert to JSON-serializable format
    session_data = []
    for session in sessions:
        responses = get_interview_responses(db, session.id)
        avg_score = sum(r.score for r in responses) / len(responses) if responses else 0
        
        session_data.append({
            "id": session.id,
            "user_id": session.user_id,
            "interview_type": session.interview_type,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "total_score": session.total_score,
            "max_score": session.max_score,
            "status": session.status,
            "question_count": len(responses),
            "average_score": round(avg_score, 2)
        })
    
    return session_data