import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from src.api.tasks import router as tasks_router
from src.api.auth import router as auth_router
from src.api.ai_chat import router as ai_chat_router
from src.api.tags import router as tags_router
from src.api.notifications import router as notifications_router
from src.database.session import engine
# Import all models so SQLModel.metadata knows about them
from src.models import (  # noqa: F401
    Task, User, ConversationMessage, ConversationHistory,
    TaskEvent, OutboxEvent, Tag, TaskTag, AuditEntry, ReminderSchedule,
)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Todo API",
    version="0.1.0",
    description="A full-featured todo list application with authentication and AI chatbot integration."
)

# Determine allowed origins based on environment
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:7860",
    "http://localhost:8000",
    "http://0.0.0.0:7860",
    "http://0.0.0.0:8000",
    "https://hackathon-todo-beryl.vercel.app",
]

# Add Hugging Face domain pattern for production
hf_space_pattern = os.getenv("HF_SPACE_URL")
if hf_space_pattern:
    allowed_origins.append(hf_space_pattern)
else:
    # Add generic pattern for Hugging Face Spaces
    allowed_origins.append("https://*.hf.space")

# Add any additional frontend URLs from environment
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(tasks_router, prefix="/api", tags=["tasks"])
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(ai_chat_router, prefix="/api", tags=["ai_chat"])
app.include_router(tags_router, prefix="/api", tags=["tags"])
app.include_router(notifications_router, prefix="/api", tags=["notifications"])

@app.on_event("startup")
def on_startup():
    """Create all database tables on startup (safe for existing tables)."""
    SQLModel.metadata.create_all(engine)


# Dapr subscription endpoint
@app.get("/dapr/subscribe")
def dapr_subscribe():
    """Tell Dapr which topics this app subscribes to."""
    return [
        {
            "pubsubname": "taskevents",
            "topic": "task-commands",
            "route": "/events/task-commands",
        }
    ]


@app.post("/events/task-commands")
def handle_task_command(event: dict):
    """Handle task.create.requested commands from recurrence service."""
    from sqlmodel import Session as SQLSession
    from src.services.task_service import TaskService
    from src.models.task import TaskCreate

    try:
        data = event.get("data", {})
        command_type = data.get("command_type", "")

        if command_type != "task.create.requested":
            return {"status": "SUCCESS"}

        task_data_raw = data.get("task_data", {})
        user_id = task_data_raw.get("user_id")
        if not user_id:
            return {"status": "DROP"}

        task_create = TaskCreate(
            title=task_data_raw.get("title", "Recurring Task"),
            description=task_data_raw.get("description"),
            priority=task_data_raw.get("priority", "medium"),
            due_date=task_data_raw.get("due_date"),
            reminder_lead_time=task_data_raw.get("reminder_lead_time", 60),
            recurrence_rule=task_data_raw.get("recurrence_rule"),
            tags=task_data_raw.get("tags"),
        )

        with SQLSession(engine) as session:
            service = TaskService(session)
            new_task = service.create_task(task_create, user_id)
            # Set recurrence_parent_id
            if task_data_raw.get("recurrence_parent_id"):
                new_task.recurrence_parent_id = task_data_raw["recurrence_parent_id"]
                session.add(new_task)
                session.commit()

        return {"status": "SUCCESS"}
    except Exception as e:
        import logging
        logging.getLogger("backend").error(f"Failed to handle task command: {e}")
        return {"status": "RETRY"}


@app.get("/")
def read_root():
    return {"message": "Todo API is running!", "status": "success"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "backend"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)