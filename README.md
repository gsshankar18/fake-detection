# fake-detection

A fake news detection application with FastAPI backend and React frontend.

## Deployment

### Using Docker Compose

1. Ensure Docker and Docker Compose are installed.
2. Run `docker-compose up --build` to build and start both services.
3. Backend will be available at http://localhost:8000
4. Frontend will be available at http://localhost:5173

### Manual Deployment

#### Backend
1. Navigate to `backend/` directory.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `uvicorn main:app --host 0.0.0.0 --port 8000`

#### Frontend
1. Navigate to `frontend/` directory.
2. Install dependencies: `npm install`
3. Build: `npm run build`
4. Serve: `npm run preview` (for production preview)