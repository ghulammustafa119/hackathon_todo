# Todo Application Setup Guide

## Backend Server (FastAPI)

The backend server is now running and properly configured:

### Starting the Backend
```bash
cd /mnt/d/Web_Development/hackathon_todo/backend
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Backend Features
- Authentication endpoints at `/api/auth/`
- Task management endpoints at `/api/tasks/`
- JWT-based authentication system
- User registration and login functionality
- Database integration with SQLModel

### Available Endpoints
- `GET /` - Health check
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/user` - Get current user (requires auth)
- `POST /api/auth/logout` - User logout
- `GET /api/tasks` - Get all tasks (requires auth)
- `POST /api/tasks` - Create new task (requires auth)
- And more task-related endpoints

## Frontend Server (Next.js)

The frontend has been fixed to properly connect with the backend:

### Starting the Frontend
```bash
cd /mnt/d/Web_Development/hackathon_todo/frontend
npm install  # Install dependencies if needed
npm run dev
```

### Frontend Fixes Applied
- Fixed incorrect import paths (`@/src/lib/auth` → `@/lib/auth`)
- Updated auth client to match backend API responses
- Corrected token handling for login/register responses
- Improved error handling for authentication flows

### Environment Configuration
Make sure to set the backend URL in your frontend environment:
```env
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8001/api/auth
```

## Authentication Flow
1. Register with email, password, and name
2. Login with email and password to get JWT token
3. Token is stored in localStorage
4. Protected routes check for valid JWT token
5. Logout clears the token from localStorage

## Testing the System
- Backend: Visit http://localhost:8001/docs for API documentation
- Backend: Visit http://localhost:8001/ for health check
- Frontend: Visit http://localhost:3000/ for the web interface

Both servers are now properly configured and ready for use!