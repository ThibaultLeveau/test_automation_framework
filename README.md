# Test Automation Framework

A comprehensive, modular test automation framework designed for technical validation of Linux and Windows systems. The framework provides a standardized approach to automate technical tests with extensible architecture and detailed reporting.

## Features

- **Modular Architecture**: Organized by testing domains (file, http, ssh, unix, etc.)
- **Cross-Platform**: Works on both Windows and Linux systems
- **JSON-Based Test Plans**: Easy-to-write test definitions
- **Dynamic Function Loading**: Automatically imports and executes test functions
- **Comprehensive Reporting**: Detailed execution reports with timestamps
- **Extensible Design**: Easy to add new test types and categories
- **Standardized Output**: Consistent return format across all tests
- **Test Case Filtering**: Execute specific test cases using `-i` option
- **Debug Levels**: Flexible debugging with `-d` option (0=no debug, 1=debug on fail, 2=debug always)
- **Help System**: Comprehensive help with `-h` option

## Quick Start

### 1. Execute Specific Test Plan (Required)

```bash
python main.py test_plans/main.json
```

### 2. Execute with Test Case Filtering

```bash
python main.py test_plans/main.json -i 1
```

### 3. Execute with Debug Output

```bash
# Debug on failures only
python main.py test_plans/main.json -d 1

# Full debug output
python main.py test_plans/main.json -d 2
```

### 4. Display Help

```bash
python main.py -h
```

### 5. Test Individual Script

```bash
python scripts/files/check_files.py main.py
```

## Project Structure

```
test-automation-framework/
├── main.py                    # Main execution engine (lightweight wrapper)
├── libs/                      # Core framework libraries
│   └── test_library.py       # Test processing and execution logic
├── scripts/                   # Test automation scripts
│   └── files/                # File system operations
│       └── check_files.py    # File validation functions
├── test_plans/               # JSON test plan definitions
│   ├── main.json            # Linux-focused test plan
│   └── windows_test.json    # Windows-focused test plan
├── docs/                     # Comprehensive documentation
│   ├── test_plan_structure.md
│   ├── script_directory_structure.md
│   └── main_script_usage.md
├── configs/                  # Framework configuration
└── tests/                    # Framework unit tests
```

## Core Components

### Test Scripts (`scripts/`)

Organized by functional categories:
- **files/**: File system operations and validations
- **http/**: HTTP/HTTPS service validations  
- **ssh/**: SSH connectivity and command execution
- **unix/**: Unix/Linux system commands
- **network/**: Network connectivity checks
- **database/**: Database connectivity and queries
- **security/**: Security-related validations
- **custom/**: Project-specific validations

### Test Plans (`test_plans/`)

JSON files defining test execution flow:
- Define test cases and steps
- Reference test functions with parameters
- Support metadata and versioning
- Automatic discovery by main.py

### Main Execution Engine (`main.py`)

- Scans and validates test plans
- Dynamically imports test functions
- Executes test steps sequentially
- Generates detailed execution reports
- Provides real-time console output

## Documentation

- **[Test Plan Structure](docs/test_plan_structure.md)** - JSON schema and examples
- **[Script Directory Structure](docs/script_directory_structure.md)** - Organization and conventions
- **[Main Script Usage](docs/main_script_usage.md)** - Command line interface and integration

## Example Test Plan

```json
{
  "name": "System Validation Test",
  "description": "Comprehensive system validation",
  "version": "1.0.0",
  "test_cases": [
    {
      "id": 1,
      "name": "File System Validation",
      "description": "Validate critical system files",
      "steps": [
        {
          "step_number": 1,
          "test_script": "files/check_files.py",
          "test_function": "check_file",
          "parameters": {
            "file_path": "/etc/passwd",
            "expected_permission": "644",
            "expected_owner": "root"
          }
        }
      ]
    }
  ]
}
```

## Standardized Return Format

All test functions return a consistent structure:

```python
{
    "stdout": "Success message",
    "stderr": "Error message if any",
    "exception": "Exception details if any",
    "returncode": 0  # 0=success, non-zero=failure
}
```

## Return Code Guidelines

- **0**: Test passed successfully
- **1**: Test failed (expected failure condition)
- **2**: Execution error (unexpected failure)
- **3**: Function import/loading error
- **4**: Parameter validation error

## Integration Examples

### Continuous Integration

```yaml
# GitHub Actions
- name: Run Test Automation
  run: python main.py
```

### Docker

```dockerfile
FROM python:3.9-slim
COPY . .
CMD ["python", "main.py"]
```

### Scheduled Execution

```bash
# Cron job (daily at 2 AM)
0 2 * * * cd /path/to/framework && python main.py
```

## Requirements

- Python 3.6 or higher
- Standard Python libraries only (no external dependencies)

## Getting Started

1. **Review Documentation**: Start with the documentation in the `docs/` directory
2. **Examine Examples**: Look at existing test plans and scripts
3. **Run Tests**: Execute the framework with `python main.py`
4. **Create Custom Tests**: Add new scripts following the established patterns
5. **Extend Framework**: Add new categories as needed for your use cases

## Best Practices

1. **Modular Design**: Keep test scripts focused on single responsibilities
2. **Parameterization**: Make tests configurable through parameters
3. **Error Handling**: Implement comprehensive error handling in scripts
4. **Documentation**: Maintain clear documentation for test plans and scripts
5. **Version Control**: Track changes to test plans and scripts
6. **Regular Execution**: Run tests regularly to catch issues early

## Support

For questions or issues:
1. Review the comprehensive documentation
2. Check existing test plans and scripts for examples
3. Examine generated execution reports for debugging

## License

This framework is designed for internal use and can be customized according to your organization's needs.
