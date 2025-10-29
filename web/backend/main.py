#!/usr/bin/env python3
"""
Test Automation Framework - Web Interface Backend
FastAPI backend for managing test plans, test catalog, execution logs, and variables.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
import json
import os
import sys
import re
from datetime import datetime

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
    author: Optional[str] = "Unknown"
    created_date: Optional[str] = None
    test_cases: List[Dict[str, Any]]

class TestExecutionRequest(BaseModel):
    test_plan_id: str
    debug_level: Optional[int] = 0

class Variable(BaseModel):
    name: str
    value: str
    description: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v:
            raise ValueError('Variable name cannot be empty')
        if ' ' in v:
            raise ValueError('Variable name cannot contain spaces')
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise ValueError('Variable name must start with a letter or underscore and contain only alphanumeric characters and underscores')
        return v

class TestFunction(BaseModel):
    script_path: str
    function_name: str
    function_args: Dict[str, str]
    description: str
    category: str
    platform_support: List[str]
    return_structure: Dict[str, str]

# Utility functions
def get_test_plans_directory():
    """Get the path to test plans directory"""
    return os.path.join(os.path.dirname(__file__), '..', '..', 'test_plans')

def get_script_catalog_path():
    """Get the path to script catalog"""
    return os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'script_catalog.json')

def generate_filename(name: str) -> str:
    """Generate filename from test plan name (convert spaces to underscores)"""
    # Convert to lowercase and replace spaces with underscores
    filename = name.lower().replace(' ', '_')
    # Remove any non-alphanumeric characters except underscores
    filename = re.sub(r'[^a-z0-9_]', '', filename)
    # Ensure it doesn't start or end with underscore
    filename = filename.strip('_')
    # Add .json extension
    return f"{filename}.json"

def validate_test_cases(test_cases: List[Dict[str, Any]]) -> bool:
    """Validate test cases structure"""
    if not isinstance(test_cases, list):
        return False
    
    for test_case in test_cases:
        if not isinstance(test_case, dict):
            return False
        # Basic validation for required fields in test cases
        if 'id' not in test_case or 'name' not in test_case or 'steps' not in test_case:
            return False
        if not isinstance(test_case['steps'], list):
            return False
    
    return True

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

def get_variables_path():
    """Get the path to variables configuration"""
    return os.path.join(os.path.dirname(__file__), '..', '..', 'configs', 'variables.json')

def load_variables():
    """Load variables from file and handle both old and new formats"""
    variables_path = get_variables_path()
    try:
        with open(variables_path, 'r') as f:
            variables_data = json.load(f)
        
        # Handle new enhanced format
        if isinstance(variables_data, dict) and "variables" in variables_data:
            return variables_data["variables"]
        
        # Handle old key-value format (backward compatibility)
        variables_list = []
        for name, value in variables_data.items():
            variables_list.append({
                "name": name,
                "value": value,
                "description": ""
            })
        return variables_list
    except FileNotFoundError:
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading variables: {str(e)}")

def save_variables(variables_list):
    """Save variables to file in enhanced format with descriptions"""
    variables_path = get_variables_path()
    try:
        # Save in enhanced format that includes descriptions
        enhanced_variables = {
            "variables": variables_list,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(variables_path, 'w') as f:
            json.dump(enhanced_variables, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving variables: {str(e)}")

@app.get("/api/variables")
async def get_variables():
    """Get all variables from configuration"""
    return load_variables()

@app.post("/api/variables")
async def create_variable(variable: Variable):
    """Create a new variable"""
    try:
        variables = load_variables()
        
        # Check if variable already exists
        for existing_var in variables:
            if existing_var["name"] == variable.name:
                raise HTTPException(status_code=400, detail="Variable with this name already exists")
        
        # Add new variable
        new_variable = {
            "name": variable.name,
            "value": variable.value,
            "description": variable.description or ""
        }
        variables.append(new_variable)
        
        # Save updated variables
        save_variables(variables)
        
        return {
            "message": "Variable created successfully",
            "variable": new_variable
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating variable: {str(e)}")

@app.put("/api/variables/{variable_name}")
async def update_variable(variable_name: str, variable: Variable):
    """Update an existing variable"""
    try:
        variables = load_variables()
        
        # Find the variable to update
        variable_index = -1
        for i, existing_var in enumerate(variables):
            if existing_var["name"] == variable_name:
                variable_index = i
                break
        
        if variable_index == -1:
            raise HTTPException(status_code=404, detail="Variable not found")
        
        # If name is being changed, check for conflicts
        if variable.name != variable_name:
            for existing_var in variables:
                if existing_var["name"] == variable.name and existing_var["name"] != variable_name:
                    raise HTTPException(status_code=400, detail="Variable with this name already exists")
        
        # Update variable
        variables[variable_index] = {
            "name": variable.name,
            "value": variable.value,
            "description": variable.description or ""
        }
        
        # Save updated variables
        save_variables(variables)
        
        return {
            "message": "Variable updated successfully",
            "variable": variables[variable_index]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating variable: {str(e)}")

@app.delete("/api/variables/{variable_name}")
async def delete_variable(variable_name: str):
    """Delete a variable"""
    try:
        variables = load_variables()
        
        # Find the variable to delete
        variable_index = -1
        for i, existing_var in enumerate(variables):
            if existing_var["name"] == variable_name:
                variable_index = i
                break
        
        if variable_index == -1:
            raise HTTPException(status_code=404, detail="Variable not found")
        
        # Remove variable
        deleted_variable = variables.pop(variable_index)
        
        # Save updated variables
        save_variables(variables)
        
        return {
            "message": "Variable deleted successfully",
            "variable": deleted_variable
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting variable: {str(e)}")

@app.post("/api/test-plans")
async def create_test_plan(test_plan: TestPlan):
    """Create a new test plan"""
    try:
        # Generate filename from name
        filename = generate_filename(test_plan.name)
        file_path = os.path.join(get_test_plans_directory(), filename)
        
        # Check if file already exists
        if os.path.exists(file_path):
            raise HTTPException(status_code=400, detail="Test plan with this name already exists")
        
        # Validate test cases structure
        if not validate_test_cases(test_plan.test_cases):
            raise HTTPException(status_code=400, detail="Invalid test cases structure")
        
        # Prepare test plan data
        test_plan_data = {
            "name": test_plan.name,
            "description": test_plan.description,
            "version": test_plan.version,
            "author": test_plan.author,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "test_cases": test_plan.test_cases
        }
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(test_plan_data, f, indent=4)
        
        return {
            "message": "Test plan created successfully",
            "id": filename.replace('.json', ''),
            "file_name": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating test plan: {str(e)}")

@app.put("/api/test-plans/{test_plan_id}")
async def update_test_plan(test_plan_id: str, test_plan: TestPlan):
    """Update an existing test plan"""
    try:
        # Check if test plan exists
        existing_path = os.path.join(get_test_plans_directory(), f"{test_plan_id}.json")
        if not os.path.exists(existing_path):
            raise HTTPException(status_code=404, detail="Test plan not found")
        
        # Validate test cases structure
        if not validate_test_cases(test_plan.test_cases):
            raise HTTPException(status_code=400, detail="Invalid test cases structure")
        
        # Generate new filename if name changed
        new_filename = generate_filename(test_plan.name)
        new_file_path = os.path.join(get_test_plans_directory(), new_filename)
        
        # If name changed and new filename conflicts with existing file
        if new_filename != f"{test_plan_id}.json" and os.path.exists(new_file_path):
            raise HTTPException(status_code=400, detail="Test plan with this name already exists")
        
        # Read existing test plan to preserve created_date
        with open(existing_path, 'r') as f:
            existing_data = json.load(f)
        
        # Prepare updated test plan data
        test_plan_data = {
            "name": test_plan.name,
            "description": test_plan.description,
            "version": test_plan.version,
            "author": test_plan.author,
            "created_date": existing_data.get("created_date", datetime.now().strftime("%Y-%m-%d")),
            "test_cases": test_plan.test_cases
        }
        
        # If filename changed, delete old file and create new one
        if new_filename != f"{test_plan_id}.json":
            os.remove(existing_path)
            file_path = new_file_path
        else:
            file_path = existing_path
        
        # Write updated data
        with open(file_path, 'w') as f:
            json.dump(test_plan_data, f, indent=4)
        
        return {
            "message": "Test plan updated successfully",
            "id": new_filename.replace('.json', ''),
            "file_name": new_filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating test plan: {str(e)}")

@app.delete("/api/test-plans/{test_plan_id}")
async def delete_test_plan(test_plan_id: str):
    """Delete a test plan"""
    try:
        file_path = os.path.join(get_test_plans_directory(), f"{test_plan_id}.json")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Test plan not found")
        
        os.remove(file_path)
        
        return {
            "message": "Test plan deleted successfully",
            "id": test_plan_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting test plan: {str(e)}")

@app.post("/api/test-catalog")
async def create_test_function(test_function: TestFunction):
    """Create a new test function in catalog"""
    try:
        catalog_path = get_script_catalog_path()
        
        # Read existing catalog
        with open(catalog_path, 'r') as f:
            catalog_data = json.load(f)
        
        # Check if function already exists
        for script in catalog_data.get("scripts", []):
            if (script["script_path"] == test_function.script_path and 
                script["function_name"] == test_function.function_name):
                raise HTTPException(status_code=400, detail="Test function already exists")
        
        # Add new function
        new_function = {
            "script_path": test_function.script_path,
            "function_name": test_function.function_name,
            "function_args": test_function.function_args,
            "description": test_function.description,
            "category": test_function.category,
            "platform_support": test_function.platform_support,
            "return_structure": test_function.return_structure
        }
        
        catalog_data["scripts"].append(new_function)
        
        # Update last_updated
        catalog_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        # Write back to file
        with open(catalog_path, 'w') as f:
            json.dump(catalog_data, f, indent=2)
        
        return {
            "message": "Test function created successfully",
            "function_name": test_function.function_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating test function: {str(e)}")

@app.put("/api/test-catalog/{function_index}")
async def update_test_function(function_index: int, test_function: TestFunction):
    """Update an existing test function in catalog"""
    try:
        catalog_path = get_script_catalog_path()
        
        # Read existing catalog
        with open(catalog_path, 'r') as f:
            catalog_data = json.load(f)
        
        # Check if function index is valid
        if function_index < 0 or function_index >= len(catalog_data.get("scripts", [])):
            raise HTTPException(status_code=404, detail="Test function not found")
        
        # Update function
        catalog_data["scripts"][function_index] = {
            "script_path": test_function.script_path,
            "function_name": test_function.function_name,
            "function_args": test_function.function_args,
            "description": test_function.description,
            "category": test_function.category,
            "platform_support": test_function.platform_support,
            "return_structure": test_function.return_structure
        }
        
        # Update last_updated
        catalog_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        # Write back to file
        with open(catalog_path, 'w') as f:
            json.dump(catalog_data, f, indent=2)
        
        return {
            "message": "Test function updated successfully",
            "function_name": test_function.function_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating test function: {str(e)}")

@app.delete("/api/test-catalog/{function_index}")
async def delete_test_function(function_index: int):
    """Delete a test function from catalog"""
    try:
        catalog_path = get_script_catalog_path()
        
        # Read existing catalog
        with open(catalog_path, 'r') as f:
            catalog_data = json.load(f)
        
        # Check if function index is valid
        if function_index < 0 or function_index >= len(catalog_data.get("scripts", [])):
            raise HTTPException(status_code=404, detail="Test function not found")
        
        # Get function name for response
        function_name = catalog_data["scripts"][function_index]["function_name"]
        
        # Remove function
        catalog_data["scripts"].pop(function_index)
        
        # Update last_updated
        catalog_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        # Write back to file
        with open(catalog_path, 'w') as f:
            json.dump(catalog_data, f, indent=2)
        
        return {
            "message": "Test function deleted successfully",
            "function_name": function_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting test function: {str(e)}")

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
