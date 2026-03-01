from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.dsa_questions import DifficultyLevel


class DSAQuestionBase(BaseModel):
    title: str
    description: str
    difficulty: DifficultyLevel
    category: str = "algorithms"
    solution: Optional[str] = None
    hints: Optional[str] = None
    estimated_time: int = 300


class DSAQuestionCreate(DSAQuestionBase):
    pass


class DSAQuestionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    category: Optional[str] = None
    solution: Optional[str] = None
    hints: Optional[str] = None
    estimated_time: Optional[int] = None
    is_active: Optional[bool] = None


class DSAQuestion(DSAQuestionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True