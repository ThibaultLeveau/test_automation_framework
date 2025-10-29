# Test Execution Interface

## Overview

The Test Execution Interface provides a web-based interface for executing test plans with real-time output streaming and automatic execution log generation.

## Features

- **Test Plan Selection**: Dropdown menu to select from available test plans
- **Real-time Output**: Live streaming of stdout and stderr from test execution
- **Execution Status**: Visual indicators for execution status (Starting, Running, Completed, Failed)
- **Automatic Log Generation**: Execution logs are automatically created with consistent naming
- **Color-coded Results**: Green for successful executions, red for failed executions
- **Execution Log Links**: Direct links to view detailed execution results

## Usage

### Accessing the Interface

1. Navigate to the "Execute Tests" section in the main navigation
2. Select a test plan from the dropdown menu
3. Click the "Execute" button to start the test execution

### Execution Flow

1. **Selection**: Choose a test plan from the available options
2. **Execution**: Click "Execute" to start the test
3. **Real-time Monitoring**: Watch the live output in the terminal-style display
4. **Completion**: View the execution status and access the execution log
5. **Results**: Click the generated link to view detailed execution results

### Execution Status Indicators

- **STARTING**: Test execution is being initialized
- **RUNNING**: Test is currently executing
- **COMPLETED**: Test finished successfully (green indicator)
- **FAILED**: Test execution failed (red indicator)

### Output Display

- **STDOUT**: Standard output from the test execution (white text)
- **STDERR**: Error output from the test execution (red text)
- **Timestamps**: Each output line includes a timestamp for tracking

## Technical Details

### Backend Integration

- Uses WebSocket connections for real-time output streaming
- Executes `main.py` with the selected test plan as argument
- Generates execution logs in the `test_execution_log/` directory
- Follows consistent filename format: `log_Test Plan Name_YYYY-MM-DD_HH_MM.json`

### Frontend Features

- Vue.js 3 with Composition API
- WebSocket client for real-time communication
- Auto-scrolling output terminal
- Responsive design with consistent styling

## Error Handling

- **Test Plan Not Found**: Displays error if selected test plan doesn't exist
- **WebSocket Connection**: Handles connection failures gracefully
- **Execution Errors**: Captures and displays execution errors
- **Invalid Links**: Provides error feedback for invalid execution log links

## File Naming Convention

Execution logs follow this naming pattern:
```
log_{Test Plan Name}_{YYYY-MM-DD}_{HH}_{MM}.json
```

Example:
```
log_Windows Test Plan_2025-10-29_16_03.json
```

## Integration Points

- Leverages existing test execution framework (`main.py`)
- Uses existing execution log viewing functionality
- Integrates with existing test plan management
- Maintains compatibility with existing execution log structure
