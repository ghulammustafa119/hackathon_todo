"""Base class for MCP tools with user ID authentication (no JWT validation)."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
from sqlmodel import Session
from pydantic import BaseModel
from fastapi import HTTPException, status

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
        # No JWT validation needed - authentication happens at API level
        pass

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
    async def execute(self, params: Dict[str, Any], token: str, user_id: Optional[str]) -> ToolResponse:
        """
        Execute the tool with the given parameters, token, and user ID.

        Args:
            params: Parameters for the tool execution
            token: JWT token for backend API calls (already validated at API level)
            user_id: User ID for authentication (already validated at API level)

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