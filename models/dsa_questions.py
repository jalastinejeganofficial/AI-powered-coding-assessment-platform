from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base
from enum import Enum as PyEnum


class DifficultyLevel(PyEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class DSAQuestion(Base):
    __tablename__ = "dsa_questions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.INTERMEDIATE)
    category = Column(String, default="algorithms")  # algorithms, data_structures, system_design, etc.
    solution = Column(Text, nullable=True)
    hints = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    estimated_time = Column(Integer, default=300)  # in seconds
    
    # New fields for input/output examples
    input_examples = Column(JSON, nullable=True)  # List of input examples
    output_examples = Column(JSON, nullable=True)  # List of corresponding output examples
    constraints = Column(Text, nullable=True)  # Problem constraints
    
    # Relationships
    interview_questions = relationship("InterviewQuestion", back_populates="question_details")

    def __repr__(self):
        return f"<DSAQuestion(id={self.id}, title='{self.title}', difficulty='{self.difficulty}')>"