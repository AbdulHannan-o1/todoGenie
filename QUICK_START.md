# Quick Start - Local Development Testing

## Problem Fixed
Tasks were not persisting due to missing `session.commit()` in backend endpoints.

## Quick Setup (One-liner)
```bash
bash setup-local-dev.sh
```

## Start Services

### Backend (Port 8000)
```bash
cd phase5/backend
source venv_local/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Port 3000)  
```bash
cd phase5/frontend
npm run dev
```

**Access**: http://localhost:3000

## Quick Test

### ✅ Test 1: Create Task
1. Click "Create Task"
2. Fill details, submit
3. **Should see**: Task appears immediately AND persists on refresh

### ✅ Test 2: Complete Task
1. Check task checkbox
2. **Should see**: Checkbox is checked AND persists on refresh

### ✅ Test 3: Update Task
1. Edit task title
2. **Should see**: Changes apply immediately AND persist on refresh

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check Python 3.11+, run `pip install -r requirements.txt` |
| Frontend won't start | Check Node 18+, run `npm install --legacy-peer-deps` |
| API errors | Verify backend running on port 8000 |
| Tasks not saving | Check backend logs for `COMMIT` statements |

## What Changed

| File | Change |
|------|--------|
| `phase5/backend/src/api/tasks.py` | Added `session.commit()` to create_task (line 40) and update_task (line 120) |
| `phase5/frontend/.env.local` | Changed backend URL to `localhost:8000` |
| `phase5/frontend/next.config.ts` | Made backend URL environment-aware |

## Commits

- `ad4f952` - Local dev setup
- `8fafb31` - Fix task creation and updates
- `f87ef69` - Fix task updates

## Deploy to Kubernetes (When Ready)

```bash
# Build images
cd phase5/backend && docker build -t todogenie-backend:latest .
cd ../frontend && docker build -t todogenie-frontend:latest .

# Update deployment
minikube kubectl -- set image deployment/todogenie-backend \
  todogenie-backend=todogenie-backend:latest -n todogenie
```

## Documentation

- Full setup guide: `LOCAL_DEVELOPMENT.md`
- Detailed analysis: Check git commits with `git log`
