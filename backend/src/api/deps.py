from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

# Define security scheme
security = HTTPBearer()

# Use BETTER_AUTH_SECRET for JWT verification (same secret Better Auth uses to sign tokens)
# Falls back to JWT_SECRET_KEY for backwards compatibility
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-default-secret-key")
SECRET_KEY = BETTER_AUTH_SECRET or JWT_SECRET_KEY
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def verify_token(token: str) -> Optional[dict]:
    """
    Verify JWT token and return user payload if valid.
    Supports both Better Auth JWT tokens and legacy FastAPI tokens.
    """
    # Try PyJWT first (handles more JWT formats)
    try:
        import jwt as pyjwt
        payload = pyjwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": True}
        )
        # Better Auth uses "sub" for user ID
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user identity",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except Exception as pyjwt_err:
        logger.debug(f"PyJWT decode failed: {pyjwt_err}")

    # Fallback to python-jose
    try:
        from jose import JWTError, jwt as jose_jwt
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user identity",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except Exception as jose_err:
        logger.warning(f"JWT verification failed: {jose_err}")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get current user from JWT token.
    Returns payload dict with at least 'sub' (user_id).
    """
    token = credentials.credentials
    user = verify_token(token)
    user["raw_token"] = token
    return user
