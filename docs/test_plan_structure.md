# Test Plan JSON Structure Documentation

## Overview

Test plans are JSON files that define the structure and execution flow of automated tests. They are stored in the `test_plans/` directory and are automatically discovered by the main execution engine.

## Standardized JSON Schema

### Root Level Structure

```json
{
  "name": "string (required)",
  "description": "string (required)",
  "version": "string (optional)",
  "author": "string (optional)",
  "created_date": "string (optional, ISO format)",
  "test_cases": [
    // Array of test case objects (required)
  ]
}
```

### Test Case Structure

```json
{
  "id": "number or string (required)",
  "name": "string (required)",
  "description": "string (required)",
  "steps": [
    // Array of test step objects (required)
  ]
}
```

### Test Step Structure

```json
{
  "step_number": "number or string (required)",
  "test_script": "string (required)",
  "test_function": "string (required)",
  "parameters": {
    // Object containing function parameters (required)
  }
}
```

## Required Fields

### Root Level
- **name**: Unique identifier for the test plan
- **description**: Brief description of what the test plan validates
- **test_cases**: Array containing one or more test cases

### Test Case Level
- **id**: Unique identifier within the test plan
- **name**: Descriptive name of the test case
- **description**: What this specific test case validates
- **steps**: Array containing one or more test steps

### Test Step Level
- **step_number**: Sequential identifier for execution order
- **test_script**: Path to the Python script relative to `scripts/` directory
- **test_function**: Name of the function to execute within the script
- **parameters**: Key-value pairs passed to the test function

## Optional Fields

- **version**: Version of the test plan (e.g., "1.0.0")
- **author**: Creator or maintainer of the test plan
- **created_date**: Creation date in ISO format (YYYY-MM-DD)

## Script Path Resolution

Test script paths are resolved relative to the `scripts/` directory:

- `"files/check_files.py"` → `scripts/files/check_files.py`
- `"http/check_http.py"` → `scripts/http/check_http.py`
- `"ssh/check_ssh.py"` → `scripts/ssh/check_ssh.py`

## Parameter Passing

Parameters are passed directly to the test function as keyword arguments. The function signature should match the parameter names defined in the test step.

## Example Test Plan

```json
{
  "name": "System Validation Test Plan",
  "description": "Comprehensive system validation including file system, network, and service checks",
  "version": "1.0.0",
  "author": "QA Team",
  "created_date": "2025-01-21",
  "test_cases": [
    {
      "id": 1,
      "name": "File System Validation",
      "description": "Validate critical system files and permissions",
      "steps": [
        {
          "step_number": 1,
          "test_script": "files/check_files.py",
          "test_function": "check_file",
          "parameters": {
            "file_path": "/etc/passwd",
            "expected_permission": "644",
            "expected_owner": "root",
            "expected_group": "root"
          }
        },
        {
          "step_number": 2,
          "test_script": "files/check_files.py",
          "test_function": "check_file",
          "parameters": {
            "file_path": "/etc/hosts",
            "expected_permission": "644"
          }
        }
      ]
    },
    {
      "id": 2,
      "name": "Network Service Validation",
      "description": "Validate network connectivity and services",
      "steps": [
        {
          "step_number": 1,
          "test_script": "http/check_http.py",
          "test_function": "check_http_service",
          "parameters": {
            "url": "http://localhost:8080",
            "expected_status": 200,
            "timeout": 30
          }
        }
      ]
    }
  ]
}
```

## Best Practices

1. **Naming Conventions**: Use descriptive names for test plans, cases, and steps
2. **Modularity**: Keep test cases focused on specific validation areas
3. **Parameterization**: Use parameters to make tests reusable across different environments
4. **Version Control**: Include version information for traceability
5. **Documentation**: Provide clear descriptions for maintainability
6. **Error Handling**: Design test functions to handle edge cases gracefully

## Validation Rules

The framework validates test plans against these rules:
- Required fields must be present
- Test script paths must be valid and accessible
- Test functions must exist in the referenced scripts
- Step numbers should be sequential (but not strictly enforced)
- Parameters must match the function signature
