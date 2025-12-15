#!/bin/bash

# Start PostgreSQL container
echo "Starting PostgreSQL container..."
docker compose -f docker-compose.yml up -d postgres

# Start backend
echo "Starting backend development server..."
cd backend
python -m venv venv
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
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
