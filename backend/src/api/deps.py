import os
import time
import logging
import json
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Define security scheme
security = HTTPBearer()

# --- JWT Secret Resolution ---
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
SECRET_KEY = BETTER_AUTH_SECRET or JWT_SECRET_KEY

if not SECRET_KEY:
    logger.critical(
        "SECURITY: No JWT secret configured! "
        "Set BETTER_AUTH_SECRET or JWT_SECRET_KEY environment variable."
    )
    SECRET_KEY = "INSECURE-DEFAULT-CHANGE-ME"

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Better Auth JWKS endpoint for EdDSA verification
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", os.getenv("FRONTEND_URL", "https://hackathon-todo-beryl.vercel.app"))
JWKS_URL = f"{BETTER_AUTH_URL}/api/auth/jwks/" if BETTER_AUTH_URL else ""

# Cache JWKS keys (refresh every 1 hour)
_jwks_cache: dict = {"keys": [], "fetched_at": 0}
JWKS_CACHE_TTL = 3600  # seconds


def _fetch_jwks() -> list:
    """Fetch JWKS from Better Auth and cache the result."""
    now = time.time()
    if _jwks_cache["keys"] and (now - _jwks_cache["fetched_at"]) < JWKS_CACHE_TTL:
        return _jwks_cache["keys"]

    if not JWKS_URL:
        return []

    try:
        import httpx
        resp = httpx.get(JWKS_URL, timeout=10, follow_redirects=True)
        resp.raise_for_status()
        data = resp.json()
        keys = data.get("keys", [])
        _jwks_cache["keys"] = keys
        _jwks_cache["fetched_at"] = now
        logger.info(f"Fetched {len(keys)} JWKS keys from {JWKS_URL}")
        return keys
    except Exception as e:
        logger.warning(f"Failed to fetch JWKS from {JWKS_URL}: {e}")
        return _jwks_cache.get("keys", [])


def _verify_with_jwks(token: str) -> dict | None:
    """
    Verify JWT using Better Auth's JWKS (EdDSA/Ed25519).
    Returns payload dict or None if verification fails.
    """
    keys = _fetch_jwks()
    if not keys:
        return None

    import jwt as pyjwt
    from jwt import PyJWK

    for key_data in keys:
        try:
            jwk = PyJWK(key_data)
            payload = pyjwt.decode(
                token,
                jwk.key,
                algorithms=["EdDSA"],
                options={"verify_exp": True},
            )
            return payload
        except Exception as e:
            logger.debug(f"JWKS key verification failed: {e}")
            continue

    return None


def verify_token(token: str) -> dict:
    """
    Verify JWT token and return payload if valid.
    1. Try Better Auth JWKS (EdDSA) first
    2. Fall back to HS256 with shared secret (for FastAPI-issued tokens)
    Raises HTTP 401 if all methods fail.
    """
    # 1. Try Better Auth JWKS (EdDSA)
    try:
        payload = _verify_with_jwks(token)
        if payload:
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
    except Exception as e:
        logger.debug(f"JWKS verification error: {e}")

    # 2. Try HS256 with shared secret (PyJWT)
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
        logger.debug(f"PyJWT HS256 decode failed: {pyjwt_err}")

    # 3. Fallback to python-jose
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
        logger.warning(f"All JWT verification methods failed: {jose_err}")

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
