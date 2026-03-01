from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    total_score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    status = Column(String, default="active")  # active, completed, cancelled
    interview_type = Column(String, default="dsa")  # dsa, behavioral, system_design, etc.
    
    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="interview_session")
    responses = relationship("InterviewResponse", back_populates="interview_session")

    def __repr__(self):
        return f"<InterviewSession(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("dsa_questions.id"), nullable=False)
    question_order = Column(Integer, nullable=False)
    asked_at = Column(DateTime(timezone=True), server_default=func.now())
    time_limit = Column(Integer, default=300)  # in seconds
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=10.0)
    
    # Relationships
    interview_session = relationship("InterviewSession", back_populates="questions")
    question_details = relationship("DSAQuestion", back_populates="interview_questions")
    responses = relationship("InterviewResponse", back_populates="interview_question")

    def __repr__(self):
        return f"<InterviewQuestion(session_id={self.interview_session_id}, question_id={self.question_id})>"


class InterviewResponse(Base):
    __tablename__ = "interview_responses"

    id = Column(Integer, primary_key=True, index=True)
    interview_session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    interview_question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False)
    response_text = Column(Text, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    ai_evaluation = Column(Text, nullable=True)
    evaluated = Column(Boolean, default=False)
    
    # New fields for code submissions
    programming_language = Column(String, nullable=True)  # Language used for submission
    execution_time = Column(Float, nullable=True)  # Time taken to solve in seconds
    
    # Scores breakdown
    technical_accuracy = Column(Float, default=0.0)
    problem_solving_logic = Column(Float, default=0.0)
    communication_clarity = Column(Float, default=0.0)
    
    # Relationships
    interview_session = relationship("InterviewSession", back_populates="responses")
    interview_question = relationship("InterviewQuestion", back_populates="responses")

    def __repr__(self):
        return f"<InterviewResponse(question_id={self.interview_question_id}, score={self.score})>"


