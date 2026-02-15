import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.tasks import router as tasks_router
from src.api.auth import router as auth_router
from src.api.ai_chat import router as ai_chat_router

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
    "http://0.0.0.0:8000"
]

# Add Hugging Face domain pattern for production
hf_space_pattern = os.getenv("HF_SPACE_URL")
if hf_space_pattern:
    allowed_origins.append(hf_space_pattern)
else:
    # Add generic pattern for Hugging Face Spaces
    allowed_origins.append("https://*.hf.space")

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