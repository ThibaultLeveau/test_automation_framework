# Script Directory Structure Documentation

## Overview

The `scripts/` directory contains all test automation scripts organized by functional categories. This modular structure allows for easy maintenance, extensibility, and clear separation of concerns.

## Directory Organization

```
scripts/
├── files/              # File system operations and validations
├── http/               # HTTP/HTTPS service validations
├── ssh/                # SSH connectivity and command execution
├── unix/               # Unix/Linux system commands and validations
├── network/            # Network connectivity and port checks
├── database/           # Database connectivity and queries
├── security/           # Security-related validations
└── custom/             # Custom or project-specific validations
```

## Category Descriptions

### files/
File system operations and validations
- File existence checks
- Permission validations
- Ownership checks
- File content validation
- Directory structure validation

**Example scripts:**
- `check_files.py` - File existence, permissions, ownership
- `validate_directory.py` - Directory structure validation
- `check_file_content.py` - File content pattern matching

### http/
HTTP/HTTPS service validations
- HTTP status code validation
- Response content validation
- API endpoint testing
- Web service availability

**Example scripts:**
- `check_http_service.py` - HTTP service availability
- `validate_api_response.py` - API response validation
- `check_ssl_certificate.py` - SSL certificate validation

### ssh/
SSH connectivity and command execution
- SSH connection testing
- Remote command execution
- SSH key validation
- Remote file operations

**Example scripts:**
- `check_ssh_connection.py` - SSH connectivity test
- `execute_remote_command.py` - Remote command execution
- `validate_ssh_keys.py` - SSH key validation

### unix/
Unix/Linux system commands and validations
- System service status
- Process monitoring
- System resource checks
- Package management validation

**Example scripts:**
- `check_service_status.py` - Service status validation
- `monitor_process.py` - Process monitoring
- `check_system_resources.py` - CPU, memory, disk checks

### network/
Network connectivity and port checks
- Port availability testing
- Network connectivity
- DNS resolution
- Network service validation

**Example scripts:**
- `check_port.py` - Port availability
- `test_network_connectivity.py` - Network connectivity
- `validate_dns.py` - DNS resolution

### database/
Database connectivity and queries
- Database connection testing
- Query execution and validation
- Database schema validation
- Data integrity checks

**Example scripts:**
- `check_database_connection.py` - Database connectivity
- `execute_database_query.py` - Query execution
- `validate_schema.py` - Schema validation

### security/
Security-related validations
- Security policy compliance
- Vulnerability checks
- Access control validation
- Security configuration

**Example scripts:**
- `check_security_policy.py` - Security policy compliance
- `validate_access_controls.py` - Access control validation
- `check_vulnerabilities.py` - Vulnerability scanning

### custom/
Custom or project-specific validations
- Application-specific tests
- Business logic validation
- Integration tests
- Custom workflows

## Script Naming Conventions

### File Names
- Use descriptive, lowercase names with underscores
- Follow the pattern: `[action]_[subject].py`
- Examples: `check_files.py`, `validate_http_service.py`, `execute_remote_command.py`

### Function Names
- Use descriptive, lowercase names with underscores
- Follow the pattern: `[action]_[subject]`
- Examples: `check_file`, `validate_service`, `execute_command`

## Script Structure Template

```python
#!/usr/bin/env python3
"""
[Category]: [Brief description of what the script does]
This script [detailed description of functionality].
"""

import os
import sys

def [function_name](param1, param2=None, param3=None):
    """
    [Brief description of what the function does]
    
    Args:
        param1 (type): Description of parameter 1
        param2 (type, optional): Description of parameter 2
        param3 (type, optional): Description of parameter 3
        
    Returns:
        dict: Standardized result structure containing:
            - stdout (str): Standard output from the test
            - stderr (str): Error output if any
            - exception (str): Exception message if any
            - returncode (int): 0 for success, non-zero for failure
    """
    
    result = {
        "stdout": "",
        "stderr": "",
        "exception": "",
        "returncode": 0
    }
    
    try:
        # Test implementation logic here
        
        # Success case
        result["stdout"] = "Test completed successfully"
        result["returncode"] = 0
        
    except Exception as e:
        result["exception"] = str(e)
        result["returncode"] = 1
    
    return result

# Optional: Direct execution support for testing
if __name__ == "__main__":
    # Parse command line arguments if needed
    # Execute function and print result
    pass
```

## Standardized Return Structure

All test functions must return a dictionary with the following structure:

```python
{
    "stdout": "string containing standard output",
    "stderr": "string containing error output",
    "exception": "string containing exception message if any",
    "returncode": 0  # 0 for success, non-zero for failure
}
```

### Return Code Guidelines
- **0**: Test passed successfully
- **1**: Test failed (expected failure condition)
- **2**: Execution error (unexpected failure)
- **3**: Function import/loading error
- **4**: Parameter validation error

## Cross-Platform Compatibility

All scripts should be designed to work on both Windows and Linux systems:
- Use `platform.system()` to detect the operating system
- Handle platform-specific code appropriately
- Use cross-platform libraries when possible
- Document platform-specific limitations

## Best Practices

1. **Single Responsibility**: Each script should focus on one specific validation area
2. **Parameterization**: Make scripts configurable through parameters
3. **Error Handling**: Implement comprehensive error handling
4. **Logging**: Provide clear output for debugging and reporting
5. **Documentation**: Include detailed docstrings and comments
6. **Testing**: Test scripts independently before integration
7. **Reusability**: Design scripts to be reusable across different test plans

## Adding New Categories

To add a new category:
1. Create the directory under `scripts/`
2. Update this documentation
3. Follow the naming conventions
4. Create template scripts for the category
5. Update test plans to reference the new category

## Example Script Implementation

```python
#!/usr/bin/env python3
"""
files: File existence and permission validation
This script checks if a file exists and validates its permissions.
"""

import os
import platform
import sys

def check_file(file_path, expected_permission=None, expected_owner=None, expected_group=None):
    """
    Check if a file exists and verify its permissions, owner, and group.
    
    Args:
        file_path (str): The path to the file to check
        expected_permission (str, optional): Expected file permission (e.g., '755')
        expected_owner (str, optional): Expected owner of the file
        expected_group (str, optional): Expected group of the file
        
    Returns:
        dict: Standardized result structure
    """
    
    result = {
        "stdout": "",
        "stderr": "",
        "exception": "",
        "returncode": 0
    }
    
    try:
        # Implementation logic here
        pass
        
    except Exception as e:
        result["exception"] = str(e)
        result["returncode"] = 2
    
    return result

if __name__ == "__main__":
    # Command-line execution support
    pass
