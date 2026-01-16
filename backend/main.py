from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.tasks import router as tasks_router
from src.api.auth import router as auth_router

app = FastAPI(title="Todo API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(auth_router, prefix="/api", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Todo API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)