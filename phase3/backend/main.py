import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from auth_utils import get_current_user, TokenData
from routes import auth, tasks

# Import chat and voice routers from the nested structure
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'phase3', 'backend'))
from phase3.backend.src.api.v1.chat import router as chat_router
from phase3.backend.src.api.v1.voice import router as voice_router

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal Server Error"},
    )

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(chat_router)
app.include_router(voice_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Todo Genie API"}

@app.get("/users/me/")
async def read_users_me(current_user: TokenData = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}, you are authenticated!"}