#!/usr/bin/env python3
"""
Test Automation Framework - Web Interface Backend
FastAPI backend for managing test plans, test catalog, execution logs, and variables.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import sys

# Add parent directory to path to import existing framework modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

app = FastAPI(
    title="Test Automation Framework API",
    description="Web interface backend for managing test automation framework",
    version="1.0.0"
)

# CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TestPlan(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    version: str = "1.0.0"
    test_cases: List[Dict[str, Any]]

class TestExecutionRequest(BaseModel):
    test_plan_id: str
    debug_level: Optional[int] = 0

class Variable(BaseModel):
    name: str
    value: str
    description: Optional[str] = None

# Utility functions
def get_test_plans_directory():
    """Get the path to test plans directory"""
    return os.path.join(os.path.dirname(__file__), '..', '..', 'test_plans')

def get_script_catalog_path():
    """Get the path to script catalog"""
    return os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'script_catalog.json')

# API Routes
@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "Test Automation Framework API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/test-plans")
async def get_test_plans():
    """Get all test plans"""
    test_plans_dir = get_test_plans_directory()
    test_plans = []
    
    try:
        for filename in os.listdir(test_plans_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(test_plans_dir, filename)
                with open(file_path, 'r') as f:
                    test_plan_data = json.load(f)
                    test_plan_data['id'] = filename.replace('.json', '')
                    test_plans.append(test_plan_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading test plans: {str(e)}")
    
    return test_plans

@app.get("/api/test-plans/{test_plan_id}")
async def get_test_plan(test_plan_id: str):
    """Get specific test plan by ID"""
    test_plan_path = os.path.join(get_test_plans_directory(), f"{test_plan_id}.json")
    
    try:
        with open(test_plan_path, 'r') as f:
            test_plan_data = json.load(f)
            test_plan_data['id'] = test_plan_id
            return test_plan_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Test plan not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading test plan: {str(e)}")

@app.get("/api/test-catalog")
async def get_test_catalog():
    """Get all available test functions from catalog"""
    catalog_path = get_script_catalog_path()
    
    try:
        with open(catalog_path, 'r') as f:
            catalog_data = json.load(f)
            return catalog_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading test catalog: {str(e)}")

@app.get("/api/variables")
async def get_variables():
    """Get all variables from configuration"""
    variables_path = os.path.join(os.path.dirname(__file__), '..', '..', 'configs', 'variables.json')
    
    try:
        with open(variables_path, 'r') as f:
            variables_data = json.load(f)
            return variables_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading variables: {str(e)}")

@app.post("/api/test-execution")
async def execute_test_plan(request: TestExecutionRequest):
    """Execute a test plan"""
    # This will be integrated with the existing test execution framework
    return {
        "message": "Test execution endpoint - will integrate with existing framework",
        "test_plan_id": request.test_plan_id,
        "debug_level": request.debug_level,
        "status": "pending"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
