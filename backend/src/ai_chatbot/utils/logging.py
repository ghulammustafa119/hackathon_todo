"""Logging utilities for agent operations."""

import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from ..config import config


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AgentLogger:
    """Custom logger for AI agent operations."""

    def __init__(self, name: str = "ai_agent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.log_level.upper()))

        # Prevent duplicate handlers
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _log_with_context(
        self,
        level: LogLevel,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ):
        """
        Log a message with optional context.

        Args:
            level: Log level
            message: Log message
            context: Additional context information
            user_id: User ID for the operation
        """
        log_entry = f"[USER:{user_id or 'UNKNOWN'}] {message}"

        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            log_entry += f" | CONTEXT: {context_str}"

        getattr(self.logger, level.value.lower())(log_entry)

    def debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ):
        """Log a debug message."""
        self._log_with_context(LogLevel.DEBUG, message, context, user_id)

    def info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ):
        """Log an info message."""
        self._log_with_context(LogLevel.INFO, message, context, user_id)

    def warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ):
        """Log a warning message."""
        self._log_with_context(LogLevel.WARNING, message, context, user_id)

    def error(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ):
        """Log an error message."""
        self._log_with_context(LogLevel.ERROR, message, context, user_id)

    def critical(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ):
        """Log a critical message."""
        self._log_with_context(LogLevel.CRITICAL, message, context, user_id)


class SecurityLogger:
    """Logger for security-related events."""

    def __init__(self):
        self.logger = AgentLogger("security")

    def log_auth_attempt(self, user_id: str, success: bool, ip_address: Optional[str] = None):
        """Log authentication attempt."""
        status = "SUCCESS" if success else "FAILED"
        context = {"result": status, "ip": ip_address} if ip_address else {"result": status}
        self.logger.info(f"Authentication {status} for user {user_id}", context=context, user_id=user_id)

    def log_token_validation(self, token_subject: str, is_valid: bool, reason: Optional[str] = None):
        """Log JWT token validation."""
        status = "VALID" if is_valid else "INVALID"
        context = {"valid": is_valid, "reason": reason} if reason else {"valid": is_valid}
        self.logger.info(f"Token validation: {status}", context=context, user_id=token_subject)

    def log_unauthorized_access(self, user_id: str, resource: str, action: str):
        """Log unauthorized access attempt."""
        context = {"resource": resource, "action": action}
        self.logger.warning(f"Unauthorized access attempt by user {user_id}", context=context, user_id=user_id)

    def log_data_access(self, user_id: str, resource: str, action: str):
        """Log data access for audit trail."""
        context = {"resource": resource, "action": action}
        self.logger.info(f"Data access: {action} on {resource}", context=context, user_id=user_id)

    def log_suspicious_activity(self, user_id: str, activity: str, details: Dict[str, Any]):
        """Log suspicious activity."""
        context = {"activity": activity, "details": details}
        self.logger.warning(f"Suspicious activity detected for user {user_id}", context=context, user_id=user_id)


# Global logger instances
agent_logger = AgentLogger()
security_logger = SecurityLogger()


def log_agent_operation(
    operation: str,
    user_id: str,
    success: bool,
    duration_ms: Optional[float] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log an agent operation.

    Args:
        operation: Name of the operation
        user_id: ID of the user performing the operation
        success: Whether the operation was successful
        duration_ms: Duration of the operation in milliseconds
        details: Additional operation details
    """
    status = "SUCCESS" if success else "FAILED"
    duration_str = f" ({duration_ms:.2f}ms)" if duration_ms else ""
    message = f"Agent operation '{operation}' {status}{duration_str}"

    context = {}
    if duration_ms is not None:
        context["duration_ms"] = duration_ms
    if details:
        context.update(details)

    agent_logger.info(message, context=context, user_id=user_id)


def log_tool_execution(
    tool_name: str,
    user_id: str,
    success: bool,
    input_params: Dict[str, Any],
    output_result: Optional[Dict[str, Any]] = None,
    error_details: Optional[str] = None
):
    """
    Log MCP tool execution.

    Args:
        tool_name: Name of the tool executed
        user_id: ID of the user triggering the tool
        success: Whether the tool execution was successful
        input_params: Input parameters to the tool
        output_result: Output result from the tool
        error_details: Error details if tool failed
    """
    status = "SUCCESS" if success else "FAILED"
    message = f"MCP tool '{tool_name}' execution {status}"

    context = {
        "tool": tool_name,
        "input_params": input_params,
        "success": success
    }

    if output_result:
        context["output_result_keys"] = list(output_result.keys()) if output_result else []
    if error_details:
        context["error"] = error_details

    agent_logger.info(message, context=context, user_id=user_id)