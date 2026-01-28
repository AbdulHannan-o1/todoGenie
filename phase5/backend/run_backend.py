#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the current working directory to Python path
sys.path.insert(0, str(Path.cwd()))

# Import and run the application
try:
    import uvicorn
    from src.main import app

    print("Starting TodoGenie backend server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
except ImportError as e:
    print(f"Failed to import application: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Failed to start server: {e}")
    sys.exit(1)