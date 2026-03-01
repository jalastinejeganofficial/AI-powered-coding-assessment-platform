from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models.user import User
from models.interview import InterviewSession, InterviewResponse
from models.dsa_questions import DSAQuestion
from schemas.user import UserCreate
import hashlib
import secrets
from typing import Optional


def get_password_hash(password: str) -> str:
    # Truncate password to 72 bytes if necessary due to bcrypt limitation
    truncated_password = password[:72] if len(password) > 72 else password
    # Use SHA-256 with salt for password hashing
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', truncated_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = pwdhash.hex()
    return salt + pwdhash


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate password to 72 bytes if necessary due to bcrypt limitation
    truncated_password = plain_password[:72] if len(plain_password) > 72 else plain_password
    # Verify password against hash
    salt = hashed_password[:32]
    stored_pwdhash = hashed_password[32:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', truncated_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = pwdhash.hex()
    return pwdhash == stored_pwdhash


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_interview_session(db: Session, session_id: int) -> Optional[InterviewSession]:
    return db.query(InterviewSession).filter(InterviewSession.id == session_id).first()


def get_user_interview_sessions(db: Session, user_id: int, limit: int = 10) -> list[InterviewSession]:
    """Get all interview sessions for a user, ordered by most recent first"""
    return db.query(InterviewSession)\
             .filter(InterviewSession.user_id == user_id)\
             .order_by(InterviewSession.started_at.desc())\
             .limit(limit).all()


def get_user_interview_count(db: Session, user_id: int) -> int:
    """Get total number of interviews for a user"""
    return db.query(InterviewSession)\
             .filter(InterviewSession.user_id == user_id)\
             .count()


def create_interview_session(db: Session, user_id: int, interview_type: str = "dsa") -> InterviewSession:
    db_session = InterviewSession(
        user_id=user_id,
        interview_type=interview_type
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_interview_responses(db: Session, session_id: int) -> list[InterviewResponse]:
    """Get all responses for an interview session"""
    return db.query(InterviewResponse)\
             .filter(InterviewResponse.interview_session_id == session_id)\
             .all()


def get_dsa_questions_by_difficulty(db: Session, difficulty, limit: int = 5) -> list[DSAQuestion]:
    from sqlalchemy import and_
    return db.query(DSAQuestion)\
             .filter(and_(DSAQuestion.difficulty == difficulty, DSAQuestion.is_active == True))\
             .limit(limit).all()


def create_interview_response(db: Session, 
                            interview_session_id: int, 
                            interview_question_id: int, 
                            response_text: str,
                            programming_language: str = None,
                            execution_time: float = None) -> InterviewResponse:
    db_response = InterviewResponse(
        interview_session_id=interview_session_id,
        interview_question_id=interview_question_id,
        response_text=response_text,
        programming_language=programming_language,
        execution_time=execution_time,
        technical_accuracy=0.0,
        problem_solving_logic=0.0,
        communication_clarity=0.0
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response


def update_interview_response_score(db: Session,
                                  response_id: int,
                                  score: float,
                                  technical_accuracy: float,
                                  problem_solving_logic: float,
                                  communication_clarity: float,
                                  feedback: str,
                                  ai_evaluation: str) -> InterviewResponse:
    db_response = db.query(InterviewResponse).filter(InterviewResponse.id == response_id).first()
    if db_response:
        db_response.score = score
        db_response.technical_accuracy = technical_accuracy
        db_response.problem_solving_logic = problem_solving_logic
        db_response.communication_clarity = communication_clarity
        db_response.feedback = feedback
        db_response.ai_evaluation = ai_evaluation
        db_response.evaluated = True
        
        # Update the parent interview session's total score
        interview_session = db.query(InterviewSession).filter(
            InterviewSession.id == db_response.interview_session_id
        ).first()
        if interview_session:
            # Recalculate total score
            total_score = db.query(InterviewResponse).filter(
                InterviewResponse.interview_session_id == interview_session.id
            ).with_entities(func.sum(InterviewResponse.score)).scalar() or 0.0
            
            interview_session.total_score = total_score
            
            # Also update user's total score
            user = db.query(User).filter(User.id == interview_session.user_id).first()
            if user:
                user.total_score += score
                user.interview_count += 1
        
        db.commit()
        db.refresh(db_response)
    return db_response