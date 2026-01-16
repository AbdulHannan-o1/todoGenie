import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import asyncio
from src.auth import get_current_user
from src.models import User
from routes import auth, tasks

# Import chat and voice routers from the flattened structure
from src.api.v1.chat import router as chat_router
from src.api.v1.voice import router as voice_router

# Import MCP server
from src.services.mcp_server.mcp_server import mcp_server

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Start the MCP server when the main application starts"""
    logger.info("Starting MCP server...")
    await mcp_server.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the MCP server when the main application shuts down"""
    logger.info("Stopping MCP server...")
    await mcp_server.stop()

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
async def read_users_me(current_user: User = Depends(get_current_user)):
    # Return user data in a format that matches the frontend's expectations
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "status": current_user.status
    }