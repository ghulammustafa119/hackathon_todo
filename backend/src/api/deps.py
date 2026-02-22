import os
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Define security scheme
security = HTTPBearer()

# --- JWT Secret Resolution ---
# BETTER_AUTH_SECRET is the primary secret (shared with Better Auth frontend).
# JWT_SECRET_KEY is a fallback for backwards compatibility.
# If NEITHER is set, log a loud warning at import time.
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
SECRET_KEY = BETTER_AUTH_SECRET or JWT_SECRET_KEY

if not SECRET_KEY:
    logger.critical(
        "SECURITY: No JWT secret configured! "
        "Set BETTER_AUTH_SECRET or JWT_SECRET_KEY environment variable. "
        "Using unsafe default - DO NOT deploy to production."
    )
    SECRET_KEY = "INSECURE-DEFAULT-CHANGE-ME"

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def verify_token(token: str) -> dict:
    """
    Verify JWT token and return payload if valid.
    Tries PyJWT first, falls back to python-jose.
    Raises HTTP 401 if invalid/expired.
    """
    # Try PyJWT first
    try:
        import jwt as pyjwt
        payload = pyjwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": True},
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user identity",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except HTTPException:
        raise
    except Exception as pyjwt_err:
        logger.debug(f"PyJWT decode failed: {pyjwt_err}")

    # Fallback to python-jose
    try:
        from jose import jwt as jose_jwt
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user identity",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except HTTPException:
        raise
    except Exception as jose_err:
        logger.warning(f"JWT verification failed: {jose_err}")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    FastAPI dependency: extract + verify JWT from Authorization header.
    Returns payload dict with at least 'sub' (user_id).
    """
    token = credentials.credentials
    payload = verify_token(token)
    payload["raw_token"] = token
    return payload
