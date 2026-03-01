from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from database.database import get_db
from models.user import User
from schemas.user import User as UserSchema


router = APIRouter()


@router.get("/", response_model=List[dict])
def get_leaderboard(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get the top users based on total score"""
    users = db.query(User)\
              .filter(User.is_active == True)\
              .order_by(desc(User.total_score))\
              .offset(offset)\
              .limit(limit)\
              .all()
    
    leaderboard = []
    rank = offset + 1
    for user in users:
        leaderboard.append({
            "rank": rank,
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "total_score": user.total_score,
            "interview_count": user.interview_count,
            "level": user.level
        })
        rank += 1
    
    return leaderboard


@router.get("/top-improvers", response_model=List[dict])
def get_top_improvers(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get users with the highest improvement in recent interviews"""
    # For now, we'll return users ordered by interview count and score
    # In a real implementation, we'd calculate improvement rate
    users = db.query(User)\
              .filter(User.is_active == True, User.interview_count > 1)\
              .order_by(desc(User.total_score / User.interview_count))\
              .limit(limit)\
              .all()
    
    improvers = []
    for user in users:
        avg_score = user.total_score / user.interview_count if user.interview_count > 0 else 0
        improvers.append({
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "total_score": user.total_score,
            "interview_count": user.interview_count,
            "average_score": round(avg_score, 2),
            "level": user.level
        })
    
    return improvers


@router.get("/by-level/{level}", response_model=List[dict])
def get_leaderboard_by_level(
    level: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get leaderboard filtered by user level"""
    users = db.query(User)\
              .filter(User.is_active == True, User.level == level)\
              .order_by(desc(User.total_score))\
              .offset(offset)\
              .limit(limit)\
              .all()
    
    leaderboard = []
    rank = offset + 1
    for user in users:
        leaderboard.append({
            "rank": rank,
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "total_score": user.total_score,
            "interview_count": user.interview_count,
            "level": user.level
        })
        rank += 1
    
    return leaderboard