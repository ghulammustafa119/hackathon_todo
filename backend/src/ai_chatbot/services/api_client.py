"""Client for connecting to Phase II backend APIs."""

import httpx
import asyncio
from typing import Any, Dict, Optional
from ..config import config


class PhaseIIBackendClient:
    """Client for connecting to Phase II backend APIs."""

    def __init__(self):
        self.base_url = config.phase_ii_backend_url
        self.timeout = httpx.Timeout(timeout=30.0, connect=5.0)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Phase II backend.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            headers: Request headers
            json_data: JSON data for request body

        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"

        # Ensure Authorization header is properly formatted
        if headers is None:
            headers = {}

        # If Authorization header exists but doesn't start with "Bearer ", add it
        if 'Authorization' in headers and not headers['Authorization'].startswith('Bearer '):
            headers['Authorization'] = f"Bearer {headers['Authorization']}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data
                )

                # Return response data
                if response.status_code in [200, 201, 204]:
                    if response.content:
                        try:
                            return response.json()
                        except Exception:
                            # If response has no content or is not JSON, return success
                            return {"success": True}
                    else:
                        return {"success": True}
                elif response.status_code == 401:
                    # Unauthorized - token invalid or expired
                    raise Exception("Authentication failed: Invalid or expired token")
                elif response.status_code == 403:
                    # Forbidden - user doesn't have permission
                    raise Exception("Access denied: Insufficient permissions")
                elif response.status_code == 404:
                    # Not found - resource doesn't exist
                    raise Exception("Resource not found")
                elif response.status_code == 422:
                    # Validation error - bad request data
                    try:
                        error_response = response.json()
                        detail = error_response.get("detail", "Validation error")
                        raise Exception(f"Validation error: {detail}")
                    except Exception:
                        raise Exception("Validation error: Invalid request data")
                else:
                    # Handle other error responses
                    error_detail = ""
                    try:
                        error_response = response.json()
                        error_detail = error_response.get("detail", str(response.text))
                    except Exception:
                        error_detail = response.text or f"HTTP {response.status_code}"

                    raise httpx.HTTPStatusError(
                        f"Backend API error: {error_detail}",
                        request=response.request,
                        response=response
                    )

            except httpx.TimeoutException:
                raise Exception("Request to backend timed out")
            except httpx.RequestError as e:
                raise Exception(f"Request to backend failed: {str(e)}")
            except Exception as e:
                # Re-raise any other exceptions
                raise e

    async def get_task(self, task_id: str, token: str) -> Dict[str, Any]:
        """
        Get a specific task.

        Args:
            task_id: ID of the task to retrieve
            token: JWT token for authentication

        Returns:
            Task data as dictionary
        """
        headers = {"Authorization": f"Bearer {token}"}
        return await self._make_request(
            method="GET",
            endpoint=f"/api/tasks/{task_id}",
            headers=headers
        )

    async def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        token: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new task.

        Args:
            title: Task title
            description: Task description (optional)
            due_date: Task due date (optional)
            token: JWT token for authentication

        Returns:
            Created task data as dictionary
        """
        headers = {"Authorization": f"Bearer {token}"}
        json_data = {
            "title": title,
            "description": description,
            "due_date": due_date
        }

        return await self._make_request(
            method="POST",
            endpoint="/api/tasks/",
            headers=headers,
            json_data=json_data
        )

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        completed: Optional[bool] = None,
        token: str = ""
    ) -> Dict[str, Any]:
        """
        Update an existing task.

        Args:
            task_id: ID of the task to update
            title: New task title (optional)
            description: New task description (optional)
            due_date: New task due date (optional)
            completed: New completion status (optional)
            token: JWT token for authentication

        Returns:
            Updated task data as dictionary
        """
        headers = {"Authorization": f"Bearer {token}"}
        json_data = {}
        if title is not None:
            json_data["title"] = title
        if description is not None:
            json_data["description"] = description
        if due_date is not None:
            json_data["due_date"] = due_date
        if completed is not None:
            json_data["completed"] = completed

        return await self._make_request(
            method="PUT",
            endpoint=f"/api/tasks/{task_id}",
            headers=headers,
            json_data=json_data
        )

    async def delete_task(self, task_id: str, token: str) -> Dict[str, Any]:
        """
        Delete a task.

        Args:
            task_id: ID of the task to delete
            token: JWT token for authentication

        Returns:
            Response data as dictionary
        """
        headers = {"Authorization": f"Bearer {token}"}
        return await self._make_request(
            method="DELETE",
            endpoint=f"/api/tasks/{task_id}",
            headers=headers
        )

    async def list_tasks(
        self,
        filter_param: Optional[str] = None,
        limit: Optional[int] = None,
        search_query: Optional[str] = None,
        token: str = ""
    ) -> Dict[str, Any]:
        """
        List tasks (filtering disabled in Phase III to comply with Stateless System Rule).

        DISABLED (Phase III): Filtering, search, and limits are disabled to comply with
        the Stateless System Rule. All tasks are returned. Deferred to Phase V.

        Args:
            filter_param: Filter by completion status ('all', 'pending', 'completed') - IGNORED in Phase III
            limit: Maximum number of tasks to return - IGNORED in Phase III
            search_query: Search term to filter tasks by title or description - IGNORED in Phase III
            token: JWT token for authentication

        Returns:
            List of tasks as dictionary
        """
        headers = {"Authorization": f"Bearer {token}"}

        # DISABLED (Phase III): Filtering is disabled to comply with the Stateless System Rule. Deferred to Phase V.
        # Build query parameters - but ignore them in Phase III
        params = {}
        # All parameters are ignored in Phase III to ensure compliance with stateless rule
        # Always fetch all tasks for the user

        return await self._make_request(
            method="GET",
            endpoint="/api/tasks/",  # Always fetch all tasks, no filtering
            headers=headers
        )

    async def toggle_task_completion(
        self,
        task_id: str,
        completed: bool,
        token: str
    ) -> Dict[str, Any]:
        """
        Toggle task completion status.

        Args:
            task_id: ID of the task to update
            completed: Desired completion status
            token: JWT token for authentication

        Returns:
            Updated task data as dictionary
        """
        headers = {"Authorization": f"Bearer {token}"}
        json_data = {"completed": completed}

        return await self._make_request(
            method="PUT",
            endpoint=f"/api/tasks/{task_id}/toggle_completion",
            headers=headers,
            json_data=json_data
        )


# Global client instance
backend_client = PhaseIIBackendClient()