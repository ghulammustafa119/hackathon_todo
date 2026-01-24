"""Base class for MCP tools with authentication validation."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
from sqlmodel import Session
from pydantic import BaseModel
from fastapi import HTTPException, status
from jose import JWTError, jwt

from ..config import config
from ..utils.validation import validate_user_ownership


logger = logging.getLogger(__name__)


class ToolResponse(BaseModel):
    """Standard response model for MCP tools."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, str]] = None
    message: str = ""


class BaseMCPTaskTool(ABC):
    """Base class for all MCP task tools."""

    def __init__(self):
        self.jwt_secret_key = config.jwt_secret_key
        self.jwt_algorithm = config.jwt_algorithm

    def _validate_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and return payload.

        Args:
            token: JWT token to validate

        Returns:
            Token payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])

            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                logger.warning("Token has expired")
                return None

            return payload
        except JWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            return None

    def _extract_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract user ID from JWT token.

        Args:
            token: JWT token to extract user ID from

        Returns:
            User ID if found, None if not found
        """
        payload = self._validate_jwt(token)
        if payload:
            return payload.get("sub")  # 'sub' typically holds the user ID in JWT
        return None

    def _validate_user_ownership_with_session(
        self,
        session: Session,
        task_id: str,
        user_id: str
    ) -> bool:
        """
        Validate that the task belongs to the user using the validation utility.

        Args:
            session: Database session
            task_id: ID of the task to check
            user_id: ID of the user making the request

        Returns:
            True if user owns the task, False otherwise
        """
        return validate_user_ownership(session, task_id, user_id)

    @abstractmethod
    def execute(self, params: Dict[str, Any], token: str) -> ToolResponse:
        """
        Execute the tool with the given parameters and token.

        Args:
            params: Parameters for the tool execution
            token: JWT token for authentication

        Returns:
            ToolResponse with success/failure status and data/error
        """
        pass

    def _handle_error(self, error_code: str, error_message: str) -> ToolResponse:
        """
        Create a standardized error response.

        Args:
            error_code: Error code
            error_message: Error message

        Returns:
            ToolResponse with error details
        """
        logger.error(f"{error_code}: {error_message}")
        return ToolResponse(
            success=False,
            error={"code": error_code, "message": error_message},
            message=error_message
        )

    def _handle_success(self, data: Dict[str, Any], message: str = "") -> ToolResponse:
        """
        Create a standardized success response.

        Args:
            data: Success data
            message: Success message

        Returns:
            ToolResponse with success data
        """
        return ToolResponse(
            success=True,
            data=data,
            message=message
        )