#!/usr/bin/env python3
"""
Proper startup script for the backend server that handles imports correctly
"""
import sys
import os

# Add the /app directory to the Python path to ensure imports work
sys.path.insert(0, '/app')

# Print debug info
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {__file__}")
print(f"Python path: {sys.path[:3]}...")  # Show first 3 paths

# Change to the /app directory to ensure proper imports
os.chdir('/app')

try:
    # Import the main app
    from src.main import app
    print("Successfully imported src.main.app")

    # Import uvicorn
    import uvicorn
    print("Successfully imported uvicorn")

    print("Starting backend server on port 8000...")
    print("Using main application from src/main.py")
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')

except ImportError as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"Runtime error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)