# Main Script Usage Documentation

## Overview

The `main.py` script is the central execution engine for the test automation framework. It automatically discovers and executes test plans from the `test_plans/` directory.

## Command Line Interface

### Basic Usage

```bash
# Execute a specific test plan (required)
python main.py test_plans/main.json

# Execute with test case filtering
python main.py test_plans/main.json -i 1

# Execute with debug output for failed steps
python main.py test_plans/main.json -d 1

# Execute with full debug output and filtering
python main.py test_plans/main.json -i 1 -d 2

# Display help
python main.py -h
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `test_plan` | Path to test plan JSON file (required) | - |
| `-i, --test-case-id ID` | Filter execution to specific test case ID | All test cases |
| `-d, --debug-level LEVEL` | Debug output level (0=no debug, 1=debug on fail, 2=debug always) | 0 |
| `-h, --help` | Show help message and exit | - |

### Debug Levels

- **Level 0 (default)**: No debug - only basic pass/fail status
- **Level 1**: Debug on fail - show STDOUT, STDERR, EXCEPTION for failed steps only
- **Level 2**: Debug always - show STDOUT, STDERR, EXCEPTION for all steps

## Execution Flow

1. **Initialization**: Framework loads and validates configuration
2. **Test Plan Discovery**: Scans `test_plans/` directory for JSON files
3. **Plan Validation**: Validates each test plan structure
4. **Function Import**: Dynamically imports test functions from scripts
5. **Test Execution**: Executes test steps in sequence
6. **Result Collection**: Captures and stores execution results
7. **Report Generation**: Creates detailed execution reports

## Output and Reporting

### Console Output

The framework provides real-time console output during execution:

```
Test Automation Framework - Starting Execution
Scanning directory: test_plans
Found 1 test plan(s)

============================================================
Executing Test Plan: Main Test Plan
Description: This is the main test plan for the project demonstrating file system checks.
Timestamp: 2025-01-21T15:40:00.123456
============================================================

Executing Test Case: File System Validation Test
Description: Validate file existence, permissions, and ownership on the system.
  Step 1: PASSED - File check passed: /etc/passwd (permissions: 644) (owner: root) (group: root)
  Step 2: PASSED - File check passed: /etc/hosts (permissions: 644)

============================================================
Test Plan Summary: Main Test Plan
Total Steps: 2
Passed: 2
Failed: 0
Success Rate: 100.0%
============================================================

################################################################################
# FINAL EXECUTION REPORT
################################################################################
Total Test Plans Executed: 1
Total Test Steps Executed: 2
Total Steps Passed: 2
Total Steps Failed: 0
Overall Success Rate: 100.0%
################################################################################
Detailed report saved to: test_execution_report_20250121_154000.json
```

### Report Files

The framework generates detailed JSON reports with timestamps:

- **Filename pattern**: `test_execution_report_YYYYMMDD_HHMMSS.json`
- **Location**: Created in the current working directory
- **Content**: Complete execution details including timestamps, results, and error information

## Return Codes

The main script returns the following exit codes:

- **0**: All test steps executed successfully
- **1**: One or more test steps failed
- **2**: Framework initialization or execution error
- **3**: No test plans found

## Environment Requirements

### Python Version
- Python 3.6 or higher

### Required Python Modules
- `os` (standard library)
- `sys` (standard library)
- `json` (standard library)
- `importlib` (standard library)
- `glob` (standard library)
- `datetime` (standard library)

### Directory Structure Requirements
```
project_root/
├── main.py
├── scripts/
│   └── [category]/
│       └── [test_script].py
└── test_plans/
    └── [test_plan].json
```

## Error Handling

### Common Error Scenarios

1. **Missing Test Plans**
   ```
   No test plan files found in test_plans directory
   ```

2. **Invalid JSON Syntax**
   ```
   Error loading test plan test_plans/invalid.json: Expecting property name enclosed in double quotes
   ```

3. **Missing Required Fields**
   ```
   Error loading test plan test_plans/incomplete.json: Missing required field: name
   ```

4. **Script Not Found**
   ```
   Error importing function check_file from files/check_files.py: Script not found: scripts/files/check_files.py
   ```

5. **Function Not Found**
   ```
   Error importing function unknown_function from files/check_files.py: Function 'unknown_function' not found in scripts/files/check_files.py
   ```

### Error Recovery

The framework continues execution even when individual test steps fail:
- Failed test steps are logged but don't stop execution
- Each test plan is executed independently
- Detailed error information is captured in reports

## Integration Examples

### Continuous Integration (CI) Integration

```yaml
# GitHub Actions example
name: Test Automation
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Run Test Automation
        run: python main.py
```

### Docker Integration

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

CMD ["python", "main.py"]
```

### Scheduled Execution

```bash
# Cron job example (runs daily at 2 AM)
0 2 * * * cd /path/to/test-automation && python main.py
```

## Advanced Usage

### Custom Test Plan Directories

To use a different test plan directory, modify the `test_plans_dir` variable in `main.py`:

```python
class TestAutomationFramework:
    def __init__(self):
        self.test_plans_dir = "custom_test_plans"  # Change this
        self.scripts_dir = "scripts"
        self.results = []
```

### Custom Script Directories

To use a different scripts directory, modify the `scripts_dir` variable:

```python
class TestAutomationFramework:
    def __init__(self):
        self.test_plans_dir = "test_plans"
        self.scripts_dir = "custom_scripts"  # Change this
        self.results = []
```

### Programmatic Usage

The framework can also be used programmatically:

```python
from main import TestAutomationFramework

# Create framework instance
framework = TestAutomationFramework()

# Execute specific test plan
results = framework.execute_test_plan("test_plans/main.json")

# Execute all test plans
framework.run_all_test_plans()

# Access results
print(f"Total steps executed: {len(framework.results)}")
```

## Performance Considerations

- **Memory Usage**: The framework loads one test script at a time to minimize memory footprint
- **Execution Time**: Each test step is executed sequentially for reliable results
- **File I/O**: Test plans and scripts are loaded on-demand to optimize performance
- **Error Isolation**: Failures in one test step don't affect subsequent steps

## Security Considerations

- **Script Execution**: Only executes Python scripts from the designated `scripts/` directory
- **Parameter Validation**: Validates test plan structure before execution
- **Path Resolution**: Uses relative paths to prevent directory traversal attacks
- **Import Safety**: Uses `importlib` for controlled module loading

## Troubleshooting

### Common Issues and Solutions

1. **"Module not found" errors**
   - Ensure all required Python modules are installed
   - Check script paths in test plans

2. **Permission denied errors**
   - Ensure execution permissions on Python scripts
   - Check file system permissions for test execution

3. **JSON parsing errors**
   - Validate JSON syntax in test plans
   - Use a JSON validator tool

4. **Function import failures**
   - Verify function names match exactly
   - Check script file paths are correct

### Debug Mode

For detailed debugging, you can modify the main script to enable verbose logging:

```python
# Add this to the execute_test_step method for debug output
print(f"DEBUG: Executing {step['test_function']} from {step['test_script']}")
print(f"DEBUG: Parameters: {step['parameters']}")
```

## Best Practices for Usage

1. **Regular Execution**: Run tests regularly to catch issues early
2. **Version Control**: Keep test plans and scripts under version control
3. **Backup Reports**: Archive execution reports for historical analysis
4. **Monitor Performance**: Track execution times to identify slow tests
5. **Update Dependencies**: Keep Python and required modules up to date
