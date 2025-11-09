"""Authentication routes: register, login, profile."""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, Token, UserProfile
from app.security import hash_password, verify_password, create_access_token, get_current_user
from app.services.audit import log_action

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    log_action(db, "user_registered", new_user, {"email": new_user.email})
    
    return new_user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Login and receive JWT token."""
    # Find user
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    # Set httpOnly cookie for web (primary auth method)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set True in production with HTTPS
        samesite="lax",
        max_age=86400,  # 1 day
        path="/"  # Ensure cookie is sent to all paths
    )
    
    log_action(db, "user_login", user)
    
    # Return token for localStorage (fallback)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    """Logout by clearing cookie."""
    response.delete_cookie("access_token", path="/")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserProfile)
def get_me(user: User = Depends(get_current_user)):
    """Get current user profile."""
    return user