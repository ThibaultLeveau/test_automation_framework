# Test Automation Framework - Web Interface

This is the web interface for the Test Automation Framework, providing a user-friendly interface to manage test plans, test catalog, test execution logs, and variable management.

## Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: VueJS 3
- **Database**: SQLite (for user data and sessions)

## Development Setup

### Backend Setup
```bash
cd web/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd web/frontend
npm install
npm run dev
```

## Features

- Test Plans Management (CRUD operations)
- Test Catalog Browser
- Test Execution Monitoring
- Variable Management
- Real-time Execution Logs
- Results Dashboard

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.
