from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from .api.auth import router as auth_router
from .api.users import router as users_router
from .api.tasks import router as tasks_router
from .api.v1.chat import router as chat_router
from .api.v1.voice import router as voice_router
from .models import User
from .db.session import get_session
from .db.engine import get_engine
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs.reminder_job import send_reminders

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    engine = get_engine()
    SQLModel.metadata.create_all(engine) # Ensure tables are created first
    scheduler = BackgroundScheduler()
    # Pass get_session as a callable so send_reminders can get a fresh session each time
    scheduler.add_job(send_reminders, 'interval', minutes=1, args=[get_session])
    scheduler.start()
    app.state.scheduler = scheduler
    yield
    # Shutdown logic
    app.state.scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(voice_router, prefix="/api/v1/voice", tags=["voice"])

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log the full exception for debugging
    import traceback
    print(f"Generic exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/protected-route")
def protected_route():
    return {"message": "This is a protected route"}
