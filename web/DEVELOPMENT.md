# Web Interface Development Guide

## Overview

This document provides development guidelines and setup instructions for the Test Automation Framework web interface.

## Architecture

The web interface follows a modern full-stack architecture:

- **Backend**: FastAPI (Python) - REST API server
- **Frontend**: VueJS 3 - Single Page Application
- **Build Tool**: Vite - Fast development and build tool
- **State Management**: Pinia - Vue state management
- **Routing**: Vue Router - Client-side routing

## Development Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r web/backend/requirements.txt
   ```

2. **Run the development server:**
   ```bash
   # From project root (Windows)
   python -m uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or from backend directory (Linux/Mac)
   cd web/backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Frontend Setup

1. **Install Node.js dependencies:**
   ```bash
   cd web/frontend
   npm install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   ```

3. **Access the web interface:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Project Structure

```
web/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main FastAPI application
│   └── requirements.txt       # Python dependencies
├── frontend/                  # VueJS frontend
│   ├── src/
│   │   ├── App.vue           # Root Vue component
│   │   ├── main.js           # Vue application entry point
│   │   ├── views/            # Page components
│   │   │   └── Home.vue      # Home page
│   │   └── components/       # Reusable components
│   ├── index.html            # HTML template
│   ├── package.json          # Node.js dependencies
│   └── vite.config.js        # Vite configuration
└── README.md                 # Project overview
```

## API Endpoints

### Current Endpoints

- `GET /` - API status
- `GET /api/test-plans` - List all test plans
- `GET /api/test-plans/{id}` - Get specific test plan
- `GET /api/test-catalog` - Get test function catalog
- `GET /api/variables` - Get all variables
- `POST /api/test-execution` - Execute test plan

### Planned Endpoints

- `POST /api/test-plans` - Create new test plan
- `PUT /api/test-plans/{id}` - Update test plan
- `DELETE /api/test-plans/{id}` - Delete test plan
- `GET /api/test-execution/{id}` - Get execution status
- `GET /api/test-execution` - List execution logs

## Development Guidelines

### Backend Development

1. **Use Pydantic models** for request/response validation
2. **Follow FastAPI conventions** for route definitions
3. **Handle errors gracefully** with appropriate HTTP status codes
4. **Use type hints** for better code documentation
5. **Add docstrings** to all functions and classes

### Frontend Development

1. **Use Composition API** with Vue 3
2. **Follow Vue style guide** for component structure
3. **Use Pinia for state management** when needed
4. **Implement responsive design** for mobile compatibility
5. **Add loading states** for async operations

### Code Style

- **Backend**: Follow PEP 8 guidelines
- **Frontend**: Use ESLint and Prettier
- **Comments**: Write clear, concise comments in English
- **Documentation**: Keep README files updated

## Integration with Existing Framework

The web interface integrates with the existing test automation framework by:

1. **Reading test plans** from the `test_plans/` directory
2. **Accessing script catalog** from `scripts/script_catalog.json`
3. **Reading variables** from `configs/variables.json`
4. **Executing tests** through the existing framework

## Testing

### Backend Testing
```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest web/backend/tests/
```

### Frontend Testing
```bash
# Install test dependencies
npm install --save-dev @vue/test-utils vitest

# Run tests
npm test
```

## Deployment

### Production Build

1. **Build frontend:**
   ```bash
   cd web/frontend
   npm run build
   ```

2. **Serve static files:**
   - The built files will be in `web/frontend/dist/`
   - Serve them with a static file server or integrate with FastAPI

### Docker Deployment

Docker configuration will be added in future phases for containerized deployment.

## Troubleshooting

### Common Issues

1. **CORS errors**: Ensure backend CORS middleware is configured correctly
2. **API connection issues**: Check if backend is running on port 8000
3. **Frontend build errors**: Clear node_modules and reinstall dependencies
4. **Import errors**: Verify Python path includes parent directories

### Debug Mode

Enable debug mode by setting environment variables:
```bash
export DEBUG=true
export LOG_LEVEL=debug
```

## Next Steps

1. Implement CRUD operations for test plans
2. Add real-time execution monitoring
3. Implement user authentication
4. Add test plan visual editor
5. Implement advanced filtering and search
6. Add reporting and analytics features
