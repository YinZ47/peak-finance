"""User profile management routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas import UserProfile, UserProfileUpdate
from app.security import get_current_user
from app.services.audit import log_action

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=UserProfile)
def get_profile(user: User = Depends(get_current_user)):
    """Get user profile."""
    return user


@router.post("", response_model=UserProfile)
def update_profile(
    updates: UserProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update user profile."""
    update_data = updates.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    log_action(db, "profile_updated", user, update_data)
    
    return user