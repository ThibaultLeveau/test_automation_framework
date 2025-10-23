#!/usr/bin/env python3
"""
Git: Git repository operations and validations
This script provides Git operations including clone, push, and delete functions
with support for authentication and Git configuration management.
"""

import os
import sys
import tempfile
from typing import Dict, Optional

def git_clone(repo_url: str, target_dir: str, clear_git_configs: bool = False, 
             auth_username: str = None, auth_password: str = None, auth_type: str = "none") -> Dict:
    """
    Clone a Git repository to the specified directory.
    
    Args:
        repo_url (str): URL of the Git repository to clone
        target_dir (str): Target directory where repository will be cloned
        clear_git_configs (bool, optional): Clear Git configuration environment variables
        auth_username (str, optional): Username for HTTP authentication
        auth_password (str, optional): Password for HTTP authentication
        auth_type (str): Authentication type - "none", "basic", "bearer", "custom" (default: "none")
        
    Returns:
        dict: Standardized result structure containing:
            - stdout (str): Standard output from the operation
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
        # Import execute_command function
        from scripts.process.execute_command import execute_command
        
        # Store original environment variables
        original_git_config_global = os.environ.get('GIT_CONFIG_GLOBAL')
        original_git_config_system = os.environ.get('GIT_CONFIG_SYSTEM')
        
        # Clear Git configs if requested
        if clear_git_configs:
            if 'GIT_CONFIG_GLOBAL' in os.environ:
                del os.environ['GIT_CONFIG_GLOBAL']
            if 'GIT_CONFIG_SYSTEM' in os.environ:
                del os.environ['GIT_CONFIG_SYSTEM']
        
        # Prepare authentication URL if credentials provided
        if auth_type == "basic" and auth_username and auth_password:
            # Convert HTTPS URL to authenticated format
            if repo_url.startswith('https://'):
                # Remove protocol and extract path
                repo_path = repo_url.replace('https://', '')
                authenticated_url = f"https://{auth_username}:{auth_password}@{repo_path}"
            else:
                authenticated_url = repo_url
        else:
            authenticated_url = repo_url
        
        # Ensure target directory exists
        os.makedirs(target_dir, exist_ok=True)
        
        # Execute git clone command using execute_command
        clone_command = f'git clone "{authenticated_url}" "{target_dir}"'
        clone_result = execute_command(clone_command, timeout=300)
        
        result["stdout"] = clone_result["stdout"]
        result["stderr"] = clone_result["stderr"]
        result["exception"] = clone_result["exception"]
        result["returncode"] = clone_result["returncode"]
        
        # Restore original environment variables
        if clear_git_configs:
            if original_git_config_global:
                os.environ['GIT_CONFIG_GLOBAL'] = original_git_config_global
            if original_git_config_system:
                os.environ['GIT_CONFIG_SYSTEM'] = original_git_config_system
        
        if clone_result["returncode"] != 0:
            result["returncode"] = 1  # Test failed
            
    except Exception as e:
        result["exception"] = str(e)
        result["returncode"] = 2  # Execution error
    
    return result


def git_push_file(repo_dir: str, file_path: str, commit_message: str, 
                 clear_git_configs: bool = False, auth_username: str = None, 
                 auth_password: str = None, auth_type: str = "none") -> Dict:
    """
    Add, commit, and push a file to a Git repository.
    
    Args:
        repo_dir (str): Path to the Git repository
        file_path (str): Path to the file to add and push
        commit_message (str): Commit message for the operation
        clear_git_configs (bool, optional): Clear Git configuration environment variables
        auth_username (str, optional): Username for HTTP authentication
        auth_password (str, optional): Password for HTTP authentication
        auth_type (str): Authentication type - "none", "basic", "bearer", "custom" (default: "none")
        
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
        # Import execute_command function
        from scripts.process.execute_command import execute_command
        
        # Store original environment variables
        original_git_config_global = os.environ.get('GIT_CONFIG_GLOBAL')
        original_git_config_system = os.environ.get('GIT_CONFIG_SYSTEM')
        
        # Clear Git configs if requested
        if clear_git_configs:
            if 'GIT_CONFIG_GLOBAL' in os.environ:
                del os.environ['GIT_CONFIG_GLOBAL']
            if 'GIT_CONFIG_SYSTEM' in os.environ:
                del os.environ['GIT_CONFIG_SYSTEM']
        
        # Verify repository exists
        if not os.path.exists(os.path.join(repo_dir, '.git')):
            result["stderr"] = f"Not a Git repository: {repo_dir}"
            result["returncode"] = 1
            return result
        
        # Verify file exists (use absolute path for verification)
        absolute_file_path = os.path.join(repo_dir, file_path) if not os.path.isabs(file_path) else file_path
        if not os.path.exists(absolute_file_path):
            result["stderr"] = f"File does not exist: {absolute_file_path}"
            result["returncode"] = 1
            return result
        
        # Add file to Git
        add_command = f'git add "{file_path}"'
        add_result = execute_command(add_command, run_location=repo_dir, timeout=60)
        
        if add_result["returncode"] != 0:
            result["stderr"] = f"Failed to add file: {add_result['stderr']}"
            result["returncode"] = 1
            return result
        
        # Commit changes
        commit_command = f'git commit -m "{commit_message}"'
        commit_result = execute_command(commit_command, run_location=repo_dir, timeout=60)
        
        if commit_result["returncode"] != 0:
            result["stderr"] = f"Failed to commit: {commit_result['stderr']}"
            result["returncode"] = 1
            return result
        
        # Push changes
        push_command = 'git push'
        push_result = execute_command(push_command, run_location=repo_dir, timeout=120)
        
        result["stdout"] = f"Add: {add_result['stdout']}\nCommit: {commit_result['stdout']}\nPush: {push_result['stdout']}"
        result["stderr"] = f"Add: {add_result['stderr']}\nCommit: {commit_result['stderr']}\nPush: {push_result['stderr']}"
        result["exception"] = f"Add: {add_result['exception']}\nCommit: {commit_result['exception']}\nPush: {push_result['exception']}"
        result["returncode"] = push_result["returncode"]
        
        # Restore original environment variables
        if clear_git_configs:
            if original_git_config_global:
                os.environ['GIT_CONFIG_GLOBAL'] = original_git_config_global
            if original_git_config_system:
                os.environ['GIT_CONFIG_SYSTEM'] = original_git_config_system
        
        if push_result["returncode"] != 0:
            result["returncode"] = 1  # Test failed
            
    except Exception as e:
        result["exception"] = str(e)
        result["returncode"] = 2  # Execution error
    
    return result


def git_validate_connectivity(repo_url: str, clear_git_configs: bool = False,
                            auth_username: str = None, auth_password: str = None, 
                            auth_type: str = "none") -> Dict:
    """
    Validate connectivity to a Git repository using ls-remote command.
    This is the Git equivalent of 'svn info' or 'svn ls' for connectivity testing.
    
    Args:
        repo_url (str): URL of the Git repository to validate
        clear_git_configs (bool, optional): Clear Git configuration environment variables
        auth_username (str, optional): Username for HTTP authentication
        auth_password (str, optional): Password for HTTP authentication
        auth_type (str): Authentication type - "none", "basic", "bearer", "custom" (default: "none")
        
    Returns:
        dict: Standardized result structure containing:
            - stdout (str): Standard output from the operation
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
        # Import execute_command function
        from scripts.process.execute_command import execute_command
        
        # Store original environment variables
        original_git_config_global = os.environ.get('GIT_CONFIG_GLOBAL')
        original_git_config_system = os.environ.get('GIT_CONFIG_SYSTEM')
        
        # Clear Git configs if requested
        if clear_git_configs:
            if 'GIT_CONFIG_GLOBAL' in os.environ:
                del os.environ['GIT_CONFIG_GLOBAL']
            if 'GIT_CONFIG_SYSTEM' in os.environ:
                del os.environ['GIT_CONFIG_SYSTEM']
        
        # Prepare authentication URL if credentials provided
        if auth_type == "basic" and auth_username and auth_password:
            # Convert HTTPS URL to authenticated format
            if repo_url.startswith('https://'):
                # Remove protocol and extract path
                repo_path = repo_url.replace('https://', '')
                authenticated_url = f"https://{auth_username}:{auth_password}@{repo_path}"
            else:
                authenticated_url = repo_url
        else:
            authenticated_url = repo_url
        
        # Execute git ls-remote command to validate connectivity
        ls_remote_command = f'git ls-remote "{authenticated_url}"'
        ls_remote_result = execute_command(ls_remote_command, timeout=60)
        
        result["stdout"] = ls_remote_result["stdout"]
        result["stderr"] = ls_remote_result["stderr"]
        result["exception"] = ls_remote_result["exception"]
        result["returncode"] = ls_remote_result["returncode"]
        
        # Restore original environment variables
        if clear_git_configs:
            if original_git_config_global:
                os.environ['GIT_CONFIG_GLOBAL'] = original_git_config_global
            if original_git_config_system:
                os.environ['GIT_CONFIG_SYSTEM'] = original_git_config_system
        
        if ls_remote_result["returncode"] != 0:
            result["returncode"] = 1  # Test failed
            
    except Exception as e:
        result["exception"] = str(e)
        result["returncode"] = 2  # Execution error
    
    return result


def git_delete_file(repo_dir: str, file_path: str, commit_message: str,
                   clear_git_configs: bool = False, auth_username: str = None,
                   auth_password: str = None, auth_type: str = "none") -> Dict:
    """
    Remove a file from a Git repository and push the deletion.
    
    Args:
        repo_dir (str): Path to the Git repository
        file_path (str): Path to the file to remove
        commit_message (str): Commit message for the operation
        clear_git_configs (bool, optional): Clear Git configuration environment variables
        auth_username (str, optional): Username for HTTP authentication
        auth_password (str, optional): Password for HTTP authentication
        auth_type (str): Authentication type - "none", "basic", "bearer", "custom" (default: "none")
        
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
        # Import execute_command function
        from scripts.process.execute_command import execute_command
        
        # Store original environment variables
        original_git_config_global = os.environ.get('GIT_CONFIG_GLOBAL')
        original_git_config_system = os.environ.get('GIT_CONFIG_SYSTEM')
        
        # Clear Git configs if requested
        if clear_git_configs:
            if 'GIT_CONFIG_GLOBAL' in os.environ:
                del os.environ['GIT_CONFIG_GLOBAL']
            if 'GIT_CONFIG_SYSTEM' in os.environ:
                del os.environ['GIT_CONFIG_SYSTEM']
        
        # Verify repository exists
        if not os.path.exists(os.path.join(repo_dir, '.git')):
            result["stderr"] = f"Not a Git repository: {repo_dir}"
            result["returncode"] = 1
            return result
        
        # Remove file from Git
        remove_command = f'git rm "{file_path}"'
        remove_result = execute_command(remove_command, run_location=repo_dir, timeout=60)
        
        if remove_result["returncode"] != 0:
            result["stderr"] = f"Failed to remove file: {remove_result['stderr']}"
            result["returncode"] = 1
            return result
        
        # Commit changes
        commit_command = f'git commit -m "{commit_message}"'
        commit_result = execute_command(commit_command, run_location=repo_dir, timeout=60)
        
        if commit_result["returncode"] != 0:
            result["stderr"] = f"Failed to commit: {commit_result['stderr']}"
            result["returncode"] = 1
            return result
        
        # Push changes
        push_command = 'git push'
        push_result = execute_command(push_command, run_location=repo_dir, timeout=120)
        
        result["stdout"] = f"Remove: {remove_result['stdout']}\nCommit: {commit_result['stdout']}\nPush: {push_result['stdout']}"
        result["stderr"] = f"Remove: {remove_result['stderr']}\nCommit: {commit_result['stderr']}\nPush: {push_result['stderr']}"
        result["exception"] = f"Remove: {remove_result['exception']}\nCommit: {commit_result['exception']}\nPush: {push_result['exception']}"
        result["returncode"] = push_result["returncode"]
        
        # Restore original environment variables
        if clear_git_configs:
            if original_git_config_global:
                os.environ['GIT_CONFIG_GLOBAL'] = original_git_config_global
            if original_git_config_system:
                os.environ['GIT_CONFIG_SYSTEM'] = original_git_config_system
        
        if push_result["returncode"] != 0:
            result["returncode"] = 1  # Test failed
            
    except Exception as e:
        result["exception"] = str(e)
        result["returncode"] = 2  # Execution error
    
    return result


# Optional: Direct execution support for testing
if __name__ == "__main__":
    # Simple test of Git functionality
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Operations Test")
    parser.add_argument("--operation", choices=["clone", "push", "delete"], required=True, help="Git operation to test")
    parser.add_argument("--repo-url", help="Repository URL for clone operation")
    parser.add_argument("--target-dir", help="Target directory for clone operation")
    parser.add_argument("--repo-dir", help="Repository directory for push/delete operations")
    parser.add_argument("--file-path", help="File path for push/delete operations")
    parser.add_argument("--commit-message", help="Commit message for push/delete operations")
    parser.add_argument("--clear-configs", action="store_true", help="Clear Git configuration")
    parser.add_argument("--auth-username", help="Authentication username")
    parser.add_argument("--auth-password", help="Authentication password")
    parser.add_argument("--auth-type", help="Authentication type", default="none")
    
    args = parser.parse_args()
    
    if args.operation == "clone":
        if not args.repo_url or not args.target_dir:
            print("Error: --repo-url and --target-dir are required for clone operation")
            sys.exit(1)
        result = git_clone(args.repo_url, args.target_dir, args.clear_configs, args.auth_username, args.auth_password, args.auth_type)
    elif args.operation == "push":
        if not args.repo_dir or not args.file_path or not args.commit_message:
            print("Error: --repo-dir, --file-path, and --commit-message are required for push operation")
            sys.exit(1)
        result = git_push_file(args.repo_dir, args.file_path, args.commit_message, args.clear_configs, args.auth_username, args.auth_password, args.auth_type)
    elif args.operation == "delete":
        if not args.repo_dir or not args.file_path or not args.commit_message:
            print("Error: --repo-dir, --file-path, and --commit-message are required for delete operation")
            sys.exit(1)
        result = git_delete_file(args.repo_dir, args.file_path, args.commit_message, args.clear_configs, args.auth_username, args.auth_password, args.auth_type)
    
    print(f"Return code: {result['returncode']}")
    print(f"Stdout: {result['stdout']}")
    if result['stderr']:
        print(f"Stderr: {result['stderr']}")
    if result['exception']:
        print(f"Exception: {result['exception']}")
    
    sys.exit(result['returncode'])
