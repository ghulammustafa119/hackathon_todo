from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from sqlmodel import Session, select
from pydantic import BaseModel, validator
from jose import jwt, JWTError
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from src.models.user import User
from src.database import get_session
from src.api.security import check_auth_rate_limit
import re

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# JWT configuration - use BETTER_AUTH_SECRET as primary (same secret Better Auth signs with)
_BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "")
SECRET_KEY = _BETTER_AUTH_SECRET or os.getenv("JWT_SECRET_KEY", "your-default-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

router = APIRouter(prefix="/auth", tags=["auth"])

# Pydantic models for auth
class UserLogin(BaseModel):
    email: str
    password: str

    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email address')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserRegister(BaseModel):
    email: str
    password: str
    name: str

    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email address')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Name cannot be empty')
        if len(v) > 100:
            raise ValueError('Name must be less than 100 characters')
        return v.strip()

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginResponse(BaseModel):
    token: str  # For frontend compatibility
    token_type: str
    user: dict  # Will contain user info

class TokenData(BaseModel):
    user_id: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # issued at time
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # Refresh tokens last longer

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=UserResponse, dependencies=[Depends(check_auth_rate_limit)])
def register_user(user_data: UserRegister, session: Session = Depends(get_session)):
    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user_data.email.lower())).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,  # Changed to 409 Conflict
            detail="User with this email already exists"
        )

    # Hash the password
    hashed_password = get_password_hash(user_data.password)

    # Create new user with normalized email and name
    db_user = User(
        email=user_data.email.lower().strip(),  # Normalize email
        password=hashed_password,
        name=user_data.name.strip()
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return UserResponse(
        id=str(db_user.id),
        email=db_user.email,
        name=db_user.name,
        created_at=db_user.created_at
    )

@router.post("/login", response_model=LoginResponse, dependencies=[Depends(check_auth_rate_limit)])
def login_user(user_credentials: UserLogin, session: Session = Depends(get_session)):
    # Find user by email with normalized email
    user = session.exec(select(User).where(User.email == user_credentials.email.lower())).first()

    if not user or not verify_password(user_credentials.password, user.password):
        # Add delay to prevent timing attacks
        import time
        time.sleep(0.1)  # Small delay to make timing consistent

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return LoginResponse(
        token=access_token,
        token_type="bearer",
        user={
            "id": str(user.id),
            "email": user.email
        }
    )

@router.post("/logout")
def logout_user():
    # In a real implementation, you might want to blacklist the token
    # For now, just return success
    return {"message": "Logged out successfully"}

@router.get("/user", response_model=UserResponse)
def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),  # Changed to use OAuth2 scheme
    session: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")

        # Verify token type
        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception

        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise credentials_exception

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        created_at=user.created_at
    )