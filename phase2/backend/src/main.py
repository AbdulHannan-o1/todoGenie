from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel
from backend.src.api.auth import router as auth_router, get_current_user
from backend.src.api.tasks import router as tasks_router
from backend.src.models.user import User
from backend.db import engine, get_session
from apscheduler.schedulers.background import BackgroundScheduler
from backend.src.jobs.reminder_job import send_reminders

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    SQLModel.metadata.create_all(engine)
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminders, 'interval', minutes=1, args=[next(get_session())])
    scheduler.start()
    app.state.scheduler = scheduler
    yield
    # Shutdown logic
    app.state.scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(tasks_router)

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
