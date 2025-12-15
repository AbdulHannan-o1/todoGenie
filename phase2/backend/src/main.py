from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel
from phase2.backend.src.api.auth import router as auth_router, get_current_user
from phase2.backend.src.api.users import router as users_router
from phase2.backend.src.api.tasks import router as tasks_router
from phase2.backend.src.models import User
from phase2.backend.src.db.session import get_session
from phase2.backend.src.db.engine import engine
from apscheduler.schedulers.background import BackgroundScheduler
from phase2.backend.src.jobs.reminder_job import send_reminders

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
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

app.include_router(auth_router)
app.include_router(tasks_router)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
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
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}, you are authenticated!"}
