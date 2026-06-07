# Local Development Setup

This guide explains how to run both the frontend and backend locally for testing without needing to rebuild Docker images and redeploy to Minikube.

## Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL client (optional, for direct database inspection)
- Git

## Quick Start

### 1. Terminal 1 - Start Backend (Port 8000)

```bash
cd phase5/backend

# Create virtual environment if not exists
python3 -m venv venv_local

# Activate virtual environment
source venv_local/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: `http://localhost:8000`

### 2. Terminal 2 - Start Frontend (Port 3000)

```bash
cd phase5/frontend

# Install dependencies (if not already done)
npm install

# Run in development mode (uses .env.local with localhost:8000)
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## API Communication

- **Frontend** runs on `http://localhost:3000`
- **Backend** runs on `http://localhost:8000`
- **API calls**: Frontend uses Next.js rewrites in `next.config.ts` to forward requests to backend
  - Client requests to `/api/...` → forwarded to `http://localhost:8000/tasks/...`
  - This is configured in `.env.local`: `NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000`

## Testing the Fixes

### Test Case 1: Create Task

1. Open `http://localhost:3000/dashboard`
2. Click "Create Task" or similar button
3. Fill in task details and submit
4. **Expected**: 
   - Success notification appears
   - Task immediately appears in the tasks table
   - Refreshing page keeps the task visible ✅

### Test Case 2: Mark Task as Complete

1. In the tasks table, check the checkbox for any task
2. **Expected**:
   - Checkbox shows as checked
   - Task shows as completed
   - Refreshing page maintains the completed status ✅

### Test Case 3: Update Task

1. Click on any task to edit it
2. Change the title or description
3. Save the changes
4. **Expected**:
   - Changes appear immediately
   - Refreshing page preserves the changes ✅

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### Backend (.env)
Uses `DATABASE_URL` pointing to Neon PostgreSQL (cloud database)

## Troubleshooting

### Backend Connection Issues
If backend doesn't start or can't connect to database:
1. Check `.env` file has valid `DATABASE_URL`
2. Ensure internet connection (Neon is cloud-hosted)
3. Check Python dependencies: `pip install -r requirements.txt`

### Frontend CORS Issues
The Next.js rewrites handle CORS, but if you see CORS errors:
1. Make sure backend is running on port 8000
2. Check `next.config.ts` for correct rewrite rules
3. Clear `.next` cache: `rm -rf .next`

### Task Creation Shows but Doesn't Persist
This was the bug we fixed! If still occurring:
1. Check backend logs for `session.commit()` statements
2. Verify database connection is working
3. Check recent commits have the fixes applied

## Deployment to Kubernetes

Once testing is complete and fixes are verified:

```bash
# Build new images
cd phase5/backend && docker build -t todogenie-backend:latest .
cd ../frontend && docker build -t todogenie-frontend:latest .

# Redeploy to Minikube
minikube kubectl -- set image deployment/todogenie-backend todogenie-backend=todogenie-backend:latest -n todogenie
minikube kubectl -- set image deployment/todogenie-frontend todogenie-frontend=todogenie-frontend:latest -n todogenie

# Verify
minikube kubectl -- rollout status deployment/todogenie-backend -n todogenie
minikube kubectl -- rollout status deployment/todogenie-frontend -n todogenie
```

## Key Files Modified

1. `.env.local` - Frontend configuration for localhost backend
2. `next.config.ts` - Environment-aware backend URL routing
3. `phase5/backend/src/api/tasks.py` - Fixed missing `session.commit()` calls

## Development Workflow

1. **Identify Issue** → Check logs
2. **Make Code Changes** → Both frontend and backend auto-reload with `--reload` flag
3. **Test Locally** → Follow "Testing the Fixes" section above
4. **Verify in Logs** → Check backend logs for database operations
5. **Commit Changes** → `git add . && git commit -m "..."`
6. **Deploy to Kubernetes** → Build images and redeploy when testing passes
