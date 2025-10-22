#!/usr/bin/env python3
"""
File Creation Test Script
This script creates files in specified locations, supporting tmp directory usage.
"""

import os
import sys


def create_file(file_path, content="", permissions=None, ensure_parent_dirs=True):
    """
    Create a file at the specified path with optional content and permissions.
    
    Args:
        file_path (str): The path where the file should be created
        content (str): Content to write to the file (optional)
        permissions (int): File permissions as octal (e.g., 0o644) (optional)
        ensure_parent_dirs (bool): Create parent directories if they don't exist
    
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
        # Ensure parent directories exist if requested
        if ensure_parent_dirs:
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
        
        # Create and write to the file
        with open(file_path, 'w') as f:
            if content:
                f.write(content)
        
        # Set permissions if specified
        if permissions is not None:
            try:
                os.chmod(file_path, permissions)
                actual_permissions = oct(os.stat(file_path).st_mode)[-3:]
                result["stdout"] = f"File created with permissions {actual_permissions}: {file_path}"
            except Exception as e:
                # On Windows, permissions may not work as expected
                result["stdout"] = f"File created: {file_path} (permission setting attempted: {permissions})"
                result["stderr"] = f"Note: Permission setting may not work as expected on Windows: {str(e)}"
        else:
            result["stdout"] = f"File created: {file_path}"
        
        # Get file info for confirmation
        file_size = os.path.getsize(file_path)
        result["stdout"] += f" (size: {file_size} bytes)"
        
        if content:
            result["stdout"] += f" with content: '{content}'"
        
        result["returncode"] = 0
        
    except Exception as e:
        result["stderr"] = f"Failed to create file {file_path}: {str(e)}"
        result["exception"] = str(e)
        result["returncode"] = 2
    
    return result


# Test function for direct execution
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        content = sys.argv[2] if len(sys.argv) > 2 else ""
        permissions = int(sys.argv[3], 8) if len(sys.argv) > 3 else None
        
        result = create_file(file_path, content, permissions)
        print(result)
    else:
        print("Usage: create_file.py <file_path> [content] [permissions]")
        print("Example: create_file.py /tmp/test.txt 'Hello World' 644")
