#!/usr/bin/env python3
"""
Script to start the backend server for the AI Chatbot with Voice Support
"""
import sys
import os

# Add the current directory to the Python path to ensure imports work
sys.path.insert(0, os.path.dirname(__file__))

# Import the main app from the outer structure (this is the real application)
from src.main import app
import uvicorn

print("Starting backend server on port 8000...")
print("Using main application from src/main.py")
uvicorn.run(app, host='0.0.0.0', port=8000)