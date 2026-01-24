"""JWT token handling utilities for agent context propagation."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import HTTPException, status
import os


def create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token with the provided data.

    Args:
        data: Data to encode in the token
        expires_delta: Expiration time delta (defaults to config value)

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Use default from env, same as auth.py approach
        minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        expire = datetime.utcnow() + timedelta(minutes=minutes)

    to_encode.update({"exp": expire})
    secret_key = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token and return its payload.
    Note: This function does not validate token type, use validate_and_extract_user_context for full validation.

    Args:
        token: JWT token string to decode

    Returns:
        Token payload if valid, None if invalid
    """
    try:
        secret_key = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        return None


def verify_token_validity(token: str) -> bool:
    """
    Verify if a JWT token is valid (not expired and properly signed).

    Args:
        token: JWT token string to verify

    Returns:
        True if valid, False if invalid/expired
    """
    decoded = decode_token(token)
    return decoded is not None


def extract_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from JWT token.

    Args:
        token: JWT token string to extract user ID from

    Returns:
        User ID if found and valid, None if not found or invalid
    """
    payload = decode_token(token)
    if payload:
        return payload.get("sub")  # 'sub' typically holds the user ID in JWT
    return None


def validate_and_extract_user_context(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate JWT token and extract user context information.
    This follows the same validation logic as Phase II authentication.

    Args:
        token: JWT token string to validate and extract context from

    Returns:
        Dictionary with user context (user_id, etc.) if valid, None if invalid
    """
    # Debug: Print to understand what's happening
    print(f"DEBUG: validate_and_extract_user_context called with token length: {len(token) if token else 0}")

    # Use the exact same loading approach as auth.py
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-default-secret-key")  # Same as auth.py
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  # Same as auth.py

    print(f"DEBUG: Using auth.py style secret key length: {len(SECRET_KEY) if SECRET_KEY else 0}")
    print(f"DEBUG: Using auth.py style algorithm: {ALGORITHM}")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"DEBUG: JWT decode successful with auth.py style, payload keys: {list(payload.keys()) if payload else 'None'}")

        # Extract user_id first (as in auth.py)
        user_id = payload.get("sub")
        print(f"DEBUG: Extracted user_id: {user_id}")

        # Verify token type (same as auth.py)
        token_type = payload.get("type")
        print(f"DEBUG: Token type: {token_type}")

        if token_type != "access":
            print(f"DEBUG: Token type mismatch. Expected 'access', got '{token_type}'")
            return None

        if user_id is None:
            print(f"DEBUG: No user_id found in payload")
            return None

        # Extract user context information
        user_context = {
            "user_id": user_id,
            "username": payload.get("username"),
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
            "type": payload.get("type")
        }

        print(f"DEBUG: Successfully validated token for user {user_id}")
        return user_context
    except JWTError as e:
        print(f"DEBUG: JWT validation error with auth.py style: {str(e)}")
        return None


def refresh_token_if_needed(token: str, threshold_minutes: int = 15) -> Optional[str]:
    """
    Refresh token if it's about to expire.

    DISABLED (Phase III): Token refresh is disabled to comply with the Stateless System Rule.
    Token lifecycle management remains the responsibility of the frontend/auth provider.
    Deferred to Phase V.

    Args:
        token: Current JWT token
        threshold_minutes: Minutes before expiration to trigger refresh

    Returns:
        Always returns None in Phase III to enforce stateless behavior.
    """
    # DISABLED (Phase III): Token refresh is disabled to comply with the Stateless System Rule.
    # Token lifecycle management remains the responsibility of the frontend/auth provider.
    # This ensures the agent remains stateless and doesn't manage auth state.
    return None