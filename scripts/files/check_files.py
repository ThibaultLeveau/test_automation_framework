import os
import platform
import stat
import sys

##
# Check file properties
# This script checks for the existence, ownership, and permissions of specified files.
##

def check_file(file_path, expected_permission=None, expected_owner=None, expected_group=None):
    """
    Check if a file exists and verify its permissions, owner, and group.
    Args:
        file_path (str): The path to the file to check.
        expected_permission (str): The expected file permission (e.g., '755'). Optional.
        expected_owner (str): The expected owner of the file. Optional.
        expected_group (str): The expected group of the file. Optional.
    Returns:
        dict: The default output structure containing stdout, stderr, exception, and returncode.
    """
    
    result = {
        "stdout": "",
        "stderr": "",
        "exception": "",
        "returncode": 0
    }
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            result["stderr"] = f"File does not exist: {file_path}"
            result["returncode"] = 1
            return result
        
        # Get file stats
        file_stat = os.stat(file_path)
        
        # Check permissions if specified
        if expected_permission:
            actual_permission = oct(file_stat.st_mode)[-3:]
            if actual_permission != expected_permission:
                result["stderr"] = f"Permission mismatch. Expected: {expected_permission}, Actual: {actual_permission}"
                result["returncode"] = 1
                return result
        
        # Check owner and group (Linux/Unix only)
        if platform.system() != "Windows":
            if expected_owner:
                import pwd
                actual_owner = pwd.getpwuid(file_stat.st_uid).pw_name
                if actual_owner != expected_owner:
                    result["stderr"] = f"Owner mismatch. Expected: {expected_owner}, Actual: {actual_owner}"
                    result["returncode"] = 1
                    return result
            
            if expected_group:
                import grp
                actual_group = grp.getgrgid(file_stat.st_gid).gr_name
                if actual_group != expected_group:
                    result["stderr"] = f"Group mismatch. Expected: {expected_group}, Actual: {actual_group}"
                    result["returncode"] = 1
                    return result
        
        # Success case
        result["stdout"] = f"File check passed: {file_path}"
        if expected_permission:
            result["stdout"] += f" (permissions: {expected_permission})"
        if expected_owner:
            result["stdout"] += f" (owner: {expected_owner})"
        if expected_group:
            result["stdout"] += f" (group: {expected_group})"
            
    except Exception as e:
        result["exception"] = str(e)
        result["returncode"] = 2
    
    return result

# Test function for direct execution
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        expected_permission = sys.argv[2] if len(sys.argv) > 2 else None
        expected_owner = sys.argv[3] if len(sys.argv) > 3 else None
        expected_group = sys.argv[4] if len(sys.argv) > 4 else None
        
        result = check_file(file_path, expected_permission, expected_owner, expected_group)
        print(result)
