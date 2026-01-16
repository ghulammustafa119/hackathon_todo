# Implementation Plan: Todo Evolution Project - Phase II

**Branch**: `002-todo-evolution` | **Date**: 2026-01-07 | **Spec**: [specs/002-todo-evolution/spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-todo-evolution/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Architecture Overview

This Phase II implementation transforms the in-memory console application into a full-stack web application with authentication and persistent storage. The architecture follows a traditional web application pattern with a Next.js frontend, FastAPI backend, and Neon PostgreSQL database. Better Auth handles user authentication with JWT token issuance, and the backend verifies these tokens for secure API access.

**System Components:**
- **Frontend**: Next.js application with App Router for routing and Better Auth integration
- **Backend**: FastAPI server with SQLModel ORM for database operations and JWT verification
- **Database**: Neon Serverless PostgreSQL for data persistence
- **Authentication**: Better Auth for user management and JWT token issuance

**Auth Flow:**
1. User authenticates via Better Auth on the frontend
2. Better Auth issues JWT token to frontend
3. Frontend includes JWT token in Authorization header for API requests
4. Backend verifies JWT token using Better Auth's verification methods
5. Backend extracts user identity from JWT and validates user-scoped operations

## Component Breakdown

### Frontend Components (Next.js)
- **Authentication Pages**: Login, register, and logout pages integrated with Better Auth
- **Task Management Pages**: Dashboard with task list, task creation form, and task update form
- **Authentication Service**: Client-side utilities for token management and auth state
- **API Service**: Client-side utilities for making authenticated API calls to backend
- **Task Components**: Reusable components for displaying and interacting with tasks

### Backend Modules (FastAPI)
- **Models**: SQLModel definitions for User and Task entities with proper relationships
- **Services**: Business logic for task operations with user-scoping validation
- **API Routes**: Secure endpoints for authentication and task management with JWT middleware
- **Dependencies**: JWT token verification and user extraction utilities
- **Database Layer**: Session management and connection pooling for Neon PostgreSQL

### API Surface Overview
- **POST /auth/login** - User login (handled by Better Auth)
- **POST /auth/logout** - User logout (handled by Better Auth)
- **GET /api/tasks** - Retrieve authenticated user's tasks
- **POST /api/tasks** - Create a task for authenticated user
- **PUT /api/tasks/{id}** - Update a task for authenticated user
- **DELETE /api/tasks/{id}** - Delete a task for authenticated user
- **PATCH /api/tasks/{id}/complete** - Toggle task completion status

## Data Model Plan

### Entities and Relationships
- **User Entity**: Managed by Better Auth with ID, email, and authentication data
- **Task Entity**: Contains title, description, completion status, timestamps, and foreign key to User
- **Relationship**: One-to-many (one user to many tasks) with proper foreign key constraints

### Ownership and Access Rules
- Each task is owned by exactly one user
- Users can only access, modify, or delete their own tasks
- Backend enforces access control by verifying user ID matches task owner

### Migration Strategy
- Phase I in-memory data will not be migrated as it's ephemeral
- New users will start with empty task lists
- Database schema will be created fresh using SQLModel migrations

## Execution Plan

### Phase 1: Foundation Setup
1. Set up project structure with backend/ and frontend/ directories
2. Configure Next.js with App Router and Better Auth integration
3. Set up FastAPI with SQLModel and Neon PostgreSQL connection
4. Implement basic JWT token verification middleware

### Phase 2: Authentication Implementation
1. Integrate Better Auth on the frontend
2. Implement protected routes that require authentication
3. Create auth service for token management
4. Test authentication flow end-to-end

### Phase 3: Core Task Functionality
1. Implement Task model with user relationship in SQLModel
2. Create API endpoints for task operations with authentication
3. Build frontend components for task management
4. Implement user-scoped access controls in backend services

### Phase 4: Integration and Testing
1. Connect frontend to backend API with proper authentication headers
2. Test user isolation to ensure users can't access others' tasks
3. Perform end-to-end testing of all functionality
4. Optimize performance and fix any issues

## Risk & Constraint Analysis

### Stateless Constraints
- Backend cannot maintain session state between requests
- All authentication must be handled via JWT tokens
- User identification must occur on each API request

### Auth Failure Scenarios
- Invalid JWT tokens should return 401 Unauthorized
- Expired tokens should redirect to login page
- Failed authentication attempts should be logged for security

### Data Consistency Considerations
- Foreign key constraints must ensure referential integrity
- Transactions may be needed for complex operations
- Proper error handling to prevent data corruption

## Constitution Compliance Checklist

- ✅ Uses mandated technology stack (Next.js, FastAPI, SQLModel, Neon PostgreSQL, Better Auth)
- ✅ Implements stateless backend architecture with JWT-based authentication
- ✅ Follows REST API design principles
- ✅ Includes proper user authentication and data isolation
- ✅ Excludes out-of-scope features (priorities, tags, search, filtering, sorting, due dates)
- ✅ Maintains separation of concerns between frontend and backend
- ✅ Follows proper project structure with clear component boundaries
