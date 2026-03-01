from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InterviewSessionBase(BaseModel):
    user_id: int
    interview_type: str = "dsa"
    

class InterviewSessionCreate(InterviewSessionBase):
    pass


class InterviewSession(InterviewSessionBase):
    id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    total_score: float
    max_score: float
    status: str

    class Config:
        from_attributes = True


class InterviewQuestionBase(BaseModel):
    interview_session_id: int
    question_id: int
    question_order: int
    time_limit: int = 300


class InterviewQuestion(InterviewQuestionBase):
    id: int
    asked_at: datetime
    score: float
    max_score: float

    class Config:
        from_attributes = True


class InterviewResponseBase(BaseModel):
    interview_session_id: int
    interview_question_id: int
    response_text: str


class InterviewResponseCreate(InterviewResponseBase):
    pass


class InterviewResponse(InterviewResponseBase):
    id: int
    submitted_at: datetime
    score: float
    feedback: Optional[str] = None
    ai_evaluation: Optional[str] = None
    evaluated: bool
    technical_accuracy: float
    problem_solving_logic: float
    communication_clarity: float

    class Config:
        from_attributes = True