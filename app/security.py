"""Security utilities: password hashing, JWT tokens."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.settings import settings
from app.db import get_db
from app.models import User

# Password hashing with explicit bcrypt rounds
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Explicit rounds, prevent auto-tuning issues
)

# JWT Bearer
security = HTTPBearer(auto_error=False)

# Algorithm
ALGORITHM = "HS256"

# Bcrypt has a 72-byte limit, so we truncate safely
MAX_PASSWORD_LENGTH = 72


def _prepare_password(password: str) -> bytes:
    """
    Prepare password for bcrypt hashing.
    Bcrypt has a 72-byte limit, so we truncate UTF-8 encoded passwords.
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > MAX_PASSWORD_LENGTH:
        # Truncate to 72 bytes (this is standard bcrypt behavior)
        password_bytes = password_bytes[:MAX_PASSWORD_LENGTH]
    return password_bytes


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with 72-byte safe truncation."""
    password_bytes = _prepare_password(password)
    return pwd_context.hash(password_bytes)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    password_bytes = _prepare_password(plain)
    return pwd_context.verify(password_bytes, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


def get_current_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None)
) -> User:
    """Get current authenticated user from JWT (bearer or cookie)."""
    token = None
    
    # Try bearer token first
    if credentials:
        token = credentials.credentials
    # Fall back to cookie
    elif access_token:
        token = access_token
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = decode_access_token(token)
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user