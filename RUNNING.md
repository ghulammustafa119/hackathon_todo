# Running the Todo Evolution Project

This document explains how to run the Todo Evolution Project with the completed Phase III - AI Chatbot Integration.

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed (for the frontend)
- OpenAI API key (for AI chatbot functionality)
- PostgreSQL database (for Phase II persistence)

## Backend Setup (Phase II & III)

### 1. Backend Installation

```bash
# Navigate to the backend directory
cd /home/mustafa/projects/hackathon_todo/backend

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/todo_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI Configuration (for Phase III AI Chatbot)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# Backend URL for API Client
PHASE_II_BACKEND_URL=http://localhost:8000

# Logging
LOG_LEVEL=INFO
```

### 3. Database Setup (Phase II)

```bash
# Run the backend to initialize the database
cd /home/mustafa/projects/hackathon_todo/backend
source venv/bin/activate
python -c "
from sqlmodel import SQLModel, create_engine
from src.models.user import User
from src.models.task import Task

# Create database tables
engine = create_engine('postgresql://username:password@localhost/todo_db')
SQLModel.metadata.create_all(engine)
print('Database tables created successfully!')
"
```

### 4. Running the Backend Server

```bash
# Activate virtual environment
cd /home/mustafa/projects/hackathon_todo/backend
source venv/bin/activate

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

## Frontend Setup (Phase II & III)

### 1. Frontend Installation

```bash
# Navigate to the frontend directory
cd /home/mustafa/projects/hackathon_todo/frontend

# Install dependencies
npm install
```

### 2. Environment Configuration

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_JWT_SECRET=your-jwt-secret
```

### 3. Running the Frontend Server

```bash
# Navigate to the frontend directory
cd /home/mustafa/projects/hackathon_todo/frontend

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Phase I - Console Application

To run the original console application:

```bash
cd /home/mustafa/projects/hackathon_todo/todo_console
python main.py
```

## Using the AI Chatbot (Phase III)

### 1. Backend API Endpoints

The AI Chatbot provides the following API endpoints:

- `POST /api/ai/chat` - Send messages to the AI chatbot
- `GET /api/ai/chat/tools` - Get available tools list

### 2. Frontend Integration

1. Navigate to `http://localhost:3000`
2. Sign up and log in to your account
3. Go to the dashboard
4. Click the "AI Chat Assistant" button to open the chat interface
5. Use natural language to manage tasks:
   - "Add a task to buy groceries tomorrow"
   - "Show me my pending tasks"
   - "Mark the meeting preparation task as done"
   - "Update my project deadline to next week"
   - "Delete my old shopping list"

### 3. Available Commands

The AI chatbot understands various natural language commands:

#### Task Creation
- "Add a task to [task title]"
- "Create a task to [task title]"
- "Make a task [task title] due tomorrow"
- "Add task [title] with description [description]"

#### Task Listing
- "Show me my tasks"
- "What do I need to do today?"
- "List my pending tasks"
- "Show completed tasks"

#### Task Updates
- "Update the [task title] to [new details]"
- "Change [task title] description to [new description]"
- "Modify the due date of [task title] to [new date]"

#### Task Completion
- "Mark [task title] as done"
- "Complete the [task title]"
- "Finish the [task title]"
- "Mark [task title] as incomplete"

#### Task Deletion
- "Delete the [task title]"
- "Remove the [task title]"
- "Erase the [task title] task"

## Development Workflow

### Running in Development Mode

For active development, run both servers simultaneously:

**Terminal 1 (Backend):**
```bash
cd /home/mustafa/projects/hackathon_todo/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd /home/mustafa/projects/hackathon_todo/frontend
npm run dev
```

### Testing the AI Chatbot

You can test the AI chatbot directly using curl:

```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "message": "Add a task to buy groceries tomorrow",
    "user_id": "your-user-id"
  }'
```

## Troubleshooting

### Common Issues

1. **OpenAI API Error**: Make sure your `OPENAI_API_KEY` is correctly set in the backend `.env` file
2. **Database Connection Error**: Verify your database URL and credentials
3. **Authentication Error**: Ensure you're logged in and passing the JWT token correctly
4. **Frontend/Backend Connection**: Check that both servers are running on their respective ports

### Checking Service Status

```bash
# Check if backend is running
curl http://localhost:8000/

# Check if AI chat endpoint is accessible
curl http://localhost:8000/api/ai/chat/tools
```

## Production Deployment

For production deployment:

1. Use environment variables for secrets
2. Set up a reverse proxy (nginx)
3. Use a production WSGI server (gunicorn)
4. Set up a production database
5. Configure SSL certificates

Example production command:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Architecture Overview

- **Phase I**: Console application in `todo_console/`
- **Phase II**: Full-stack web app with backend in `backend/` and frontend in `frontend/`
- **Phase III**: AI Chatbot integration in `backend/src/ai_chatbot/`
- **MCP Tools**: Located in `backend/src/ai_chatbot/tools/`
- **AI Agent**: Located in `backend/src/ai_chatbot/agents/`
- **Frontend Chat Component**: Located in `frontend/src/components/chat/`