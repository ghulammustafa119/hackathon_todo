from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
from jose import JWTError, jwt
from src.models.task import Task
from sqlmodel import Session
from src.database import get_session

# Define security scheme
security = HTTPBearer()

# Get secret key from environment
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-default-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def verify_token(token: str) -> Optional[dict]:
    """
    Verify JWT token and return user payload if valid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get current user from JWT token
    """
    token = credentials.credentials
    user = verify_token(token)
    # Attach the raw token to the user context for tools that need it
    user["raw_token"] = token
    return user

