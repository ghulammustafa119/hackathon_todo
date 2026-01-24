# MCP Tools API Specification

## Overview
This document defines the API contracts for MCP tools used by the AI Chatbot agent. Each tool provides a specific capability for managing user tasks while maintaining stateless operation and proper user scoping.

## create_task Tool

**Tool Name:** `create_task`

**Purpose:** Create a new task in the user's task list based on extracted parameters from natural language input.

**Inputs Schema:**
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Title of the task to be created"
    },
    "description": {
      "type": "string",
      "description": "Optional description of the task"
    },
    "due_date": {
      "type": "string",
      "description": "Optional due date in ISO 8601 format (YYYY-MM-DD)"
    }
  },
  "required": ["title"]
}
```

**Output Contract:**
- Success: `{ "success": true, "task": { "id": "string", "title": "string", "description": "string", "completed": false, "created_at": "timestamp", "updated_at": "timestamp" }, "message": "Task created successfully" }`
- Failure: `{ "success": false, "error": { "code": "string", "message": "string" }, "message": "Human-readable error message" }`

**Authentication & User Scoping Rules:**
- Tool requires valid JWT authentication token passed in the agent context
- Tool operates exclusively within the scope of the authenticated user's tasks
- Tool validates user permissions before attempting task creation
- Tool rejects requests with invalid or expired authentication tokens

**Error Scenarios:**
- Invalid authentication token
- Missing required title parameter
- Malformed due_date format
- Database connection failure
- User task quota exceeded
- Server-side validation errors

## list_tasks Tool

**Tool Name:** `list_tasks`

**Purpose:** Retrieve tasks from the user's task list with optional filtering capabilities.

**Inputs Schema:**
```json
{
  "type": "object",
  "properties": {
    "filter": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "description": "Filter tasks by completion status"
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of tasks to return (default: 10, max: 100)"
    },
    "search_query": {
      "type": "string",
      "description": "Optional search term to filter tasks by title or description"
    }
  }
}
```

**Output Contract:**
- Success: `{ "success": true, "tasks": [{ "id": "string", "title": "string", "description": "string", "completed": boolean, "created_at": "timestamp", "updated_at": "timestamp" }], "total_count": integer, "message": "Tasks retrieved successfully" }`
- Failure: `{ "success": false, "error": { "code": "string", "message": "string" }, "message": "Human-readable error message" }`

**Authentication & User Scoping Rules:**
- Tool requires valid JWT authentication token passed in the agent context
- Tool returns only tasks belonging to the authenticated user
- Tool validates user permissions before returning any task data
- Tool enforces proper user isolation to prevent cross-user data access

**Error Scenarios:**
- Invalid authentication token
- Database connection failure
- Unauthorized access attempt to another user's tasks
- Invalid filter parameter values
- Server-side query errors

## update_task Tool

**Tool Name:** `update_task`

**Purpose:** Update an existing task in the user's task list with new values for specified properties.

**Inputs Schema:**
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "ID of the task to update"
    },
    "title": {
      "type": "string",
      "description": "New title for the task (optional)"
    },
    "description": {
      "type": "string",
      "description": "New description for the task (optional)"
    },
    "due_date": {
      "type": "string",
      "description": "New due date in ISO 8601 format (optional)"
    },
    "completed": {
      "type": "boolean",
      "description": "New completion status (optional)"
    }
  },
  "required": ["task_id"]
}
```

**Output Contract:**
- Success: `{ "success": true, "task": { "id": "string", "title": "string", "description": "string", "completed": boolean, "created_at": "timestamp", "updated_at": "timestamp" }, "message": "Task updated successfully" }`
- Failure: `{ "success": false, "error": { "code": "string", "message": "string" }, "message": "Human-readable error message" }`

**Authentication & User Scoping Rules:**
- Tool requires valid JWT authentication token passed in the agent context
- Tool validates that the specified task belongs to the authenticated user
- Tool prevents unauthorized modifications to tasks owned by other users
- Tool rejects requests if the task does not exist or is not accessible to the user

**Error Scenarios:**
- Invalid authentication token
- Task not found or doesn't belong to the authenticated user
- Invalid task ID format
- Database connection failure
- Invalid property values
- Server-side validation errors

## delete_task Tool

**Tool Name:** `delete_task`

**Purpose:** Permanently delete an existing task from the user's task list.

**Inputs Schema:**
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "ID of the task to delete"
    }
  },
  "required": ["task_id"]
}
```

**Output Contract:**
- Success: `{ "success": true, "task_id": "string", "message": "Task deleted successfully" }`
- Failure: `{ "success": false, "error": { "code": "string", "message": "string" }, "message": "Human-readable error message" }`

**Authentication & User Scoping Rules:**
- Tool requires valid JWT authentication token passed in the agent context
- Tool validates that the specified task belongs to the authenticated user
- Tool prevents unauthorized deletion of tasks owned by other users
- Tool rejects requests if the task does not exist or is not accessible to the user

**Error Scenarios:**
- Invalid authentication token
- Task not found or doesn't belong to the authenticated user
- Invalid task ID format
- Database connection failure
- Server-side deletion errors
- Attempt to delete protected or system tasks

## complete_task Tool

**Tool Name:** `complete_task`

**Purpose:** Toggle or set the completion status of a task in the user's task list.

**Inputs Schema:**
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "ID of the task to update completion status"
    },
    "completed": {
      "type": "boolean",
      "description": "Desired completion status (true for completed, false for incomplete)"
    }
  },
  "required": ["task_id", "completed"]
}
```

**Output Contract:**
- Success: `{ "success": true, "task": { "id": "string", "title": "string", "description": "string", "completed": boolean, "created_at": "timestamp", "updated_at": "timestamp" }, "message": "Task completion status updated successfully" }`
- Failure: `{ "success": false, "error": { "code": "string", "message": "string" }, "message": "Human-readable error message" }`

**Authentication & User Scoping Rules:**
- Tool requires valid JWT authentication token passed in the agent context
- Tool validates that the specified task belongs to the authenticated user
- Tool prevents unauthorized modification of tasks owned by other users
- Tool rejects requests if the task does not exist or is not accessible to the user

**Error Scenarios:**
- Invalid authentication token
- Task not found or doesn't belong to the authenticated user
- Invalid task ID format
- Database connection failure
- Invalid completion status value
- Server-side update errors