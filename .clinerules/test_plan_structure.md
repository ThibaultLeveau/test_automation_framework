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

### Example

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
        }
        ]
    }
    ]