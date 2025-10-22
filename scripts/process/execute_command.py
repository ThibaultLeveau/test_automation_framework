#!/usr/bin/env python3
"""
Process: Execute local commands
This script executes local commands on Windows (PowerShell) or Linux (bash) systems.
It supports command execution with optional working directory, timeout, and search string validation.
"""

import os
import platform
import subprocess
import sys

def execute_command(command, run_location=None, timeout=30, search_string=None):
    """
    Execute a local command and return the result.
    
    Args:
        command (str): The command to execute (required)
        run_location (str, optional): Working directory for command execution
        timeout (int, optional): Command timeout in seconds (default=30)
        search_string (str, optional): String to search for in stdout/stderr
        
    Returns:
        dict: Standardized result structure containing:
            - stdout (str): Standard output from the command
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
        # Validate required parameters
        if not command:
            result["stderr"] = "Command parameter is required"
            result["returncode"] = 4
            return result
        
        # Set up command execution based on platform
        current_platform = platform.system()
        
        if current_platform == "Windows":
            # Use PowerShell on Windows
            shell_command = ["powershell", "-Command", command]
        else:
            # Use bash on Linux/Unix systems
            shell_command = ["bash", "-c", command]
        
        # Set working directory if specified
        working_dir = None
        if run_location and run_location != "None":
            if not os.path.exists(run_location):
                result["stderr"] = f"Working directory does not exist: {run_location}"
                result["returncode"] = 4
                return result
            if not os.path.isdir(run_location):
                result["stderr"] = f"Working directory is not a directory: {run_location}"
                result["returncode"] = 4
                return result
            working_dir = run_location
        
        # Execute the command
        process = subprocess.run(
            shell_command,
            cwd=working_dir,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        # Capture results
        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        result["returncode"] = process.returncode
        
        # Check for search string if specified
        if search_string:
            # Normalize output and search string for comparison
            normalized_stdout = result["stdout"].strip().replace('\r\n', ' ').replace('\n', ' ')
            normalized_stderr = result["stderr"].strip().replace('\r\n', ' ').replace('\n', ' ')
            normalized_search = search_string.strip()
            
            found_in_stdout = normalized_search in normalized_stdout
            found_in_stderr = normalized_search in normalized_stderr
            
            if not found_in_stdout and not found_in_stderr:
                result["stderr"] += f"\nSearch string '{search_string}' not found in output"
                result["returncode"] = 1  # Test failed due to missing search string
        
        # Success case
        if result["returncode"] == 0 and (not search_string or (found_in_stdout or found_in_stderr)):
            result["stdout"] = f"Command executed successfully: {command}"
            if search_string:
                result["stdout"] += f" (search string '{search_string}' found)"
            
    except subprocess.TimeoutExpired:
        result["exception"] = f"Command timed out after {timeout} seconds"
        result["returncode"] = 2
    except FileNotFoundError as e:
        result["exception"] = f"Command or shell not found: {str(e)}"
        result["returncode"] = 2
    except Exception as e:
        result["exception"] = str(e)
        result["returncode"] = 2
    
    return result

# Test function for direct execution
if __name__ == "__main__":
    # Parse command line arguments for testing
    if len(sys.argv) > 1:
        command = sys.argv[1]
        run_location = sys.argv[2] if len(sys.argv) > 2 else None
        timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        search_string = sys.argv[4] if len(sys.argv) > 4 else None
        
        result = execute_command(command, run_location, timeout, search_string)
        print(result)
    else:
        # Example usage
        print("Usage: python execute_command.py <command> [run_location] [timeout] [search_string]")
        print("Example: python execute_command.py 'echo hello world' None 30 'hello'")
