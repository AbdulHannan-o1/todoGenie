#!/bin/bash


# Start backend
echo "Starting backend development server..."
cd backend
# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    python -m venv venv
fi
source venv/bin/activate
# Install dependencies if not already installed
pip install -r requirements.txt
# Start the backend server with the correct module path
uvicorn src.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting frontend development server..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Frontend (PID: $FRONTEND_PID) and Backend (PID: $BACKEND_PID) servers are running."
echo "Press Ctrl+C to stop both servers."

# Wait for both processes to finish
wait $FRONTEND_PID
wait $BACKEND_PID
