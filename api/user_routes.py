from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from models.user import User
from schemas.user import User as UserSchema, UserCreate
from utils.database_utils import (
    get_user_by_username,
    get_user_by_email,
    create_user,
    get_user,
    verify_password
)


router = APIRouter()


@router.post("/", response_model=UserSchema)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user with username already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if user with email already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create the user
    db_user = create_user(db, user)
    return db_user


@router.get("/{user_id}", response_model=UserSchema)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@router.get("/username/{username}", response_model=UserSchema)
def get_user_by_username_endpoint(username: str, db: Session = Depends(get_db)):
    """Get user by username"""
    db_user = get_user_by_username(db, username=username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@router.post("/login", response_model=UserSchema)
def login_user(user_data: dict, db: Session = Depends(get_db)):
    """Login user with username/email and password"""
    username_or_email = user_data.get("username_or_email")
    password = user_data.get("password")
    
    if not username_or_email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username/email and password are required"
        )
    
    # Try to find user by email first
    db_user = get_user_by_email(db, username_or_email)
    if not db_user:
        # If not found by email, try by username
        db_user = get_user_by_username(db, username_or_email)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Return user data (without password)
    return db_user


@router.get("/", response_model=UserSchema)
def get_user_by_email_or_username(email: str = None, username: str = None, db: Session = Depends(get_db)):
    """Get user by email or username (query parameters)"""
    if email:
        db_user = get_user_by_email(db, email=email)
    elif username:
        db_user = get_user_by_username(db, username=username)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or username parameter is required"
        )
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user