# Git Testing Documentation

## Overview

The Git testing module provides comprehensive Git repository operations for test automation, including clone, push, and delete operations with support for authentication and Git configuration management.

## Available Functions

### git_clone
Clones a Git repository to the specified directory with support for authentication and Git configuration management.

**Parameters:**
- `repo_url` (str, required): URL of the Git repository to clone
- `target_dir` (str, required): Target directory where repository will be cloned
- `clear_git_configs` (bool, optional): Clear Git configuration environment variables (default: false)
- `auth_username` (str, optional): Username for HTTP authentication
- `auth_token` (str, optional): Token for HTTP authentication

**Example:**
```json
{
  "test_script": "git/git_operations.py",
  "test_function": "git_clone",
  "authentication": {
    "authentication_type": "basic",
    "authentication_name": "github_test_private_repo"
  },
  "parameters": {
    "repo_url": "https://github.com/ThibaultLeveau/test_private_repo.git",
    "target_dir": "<tmp>/test_private_repo",
    "clear_git_configs": true
  }
}
```

### git_push_file
Adds, commits, and pushes a file to a Git repository with support for authentication and Git configuration management.

**Parameters:**
- `repo_dir` (str, required): Path to the Git repository
- `file_path` (str, required): Path to the file to add and push
- `commit_message` (str, required): Commit message for the operation
- `clear_git_configs` (bool, optional): Clear Git configuration environment variables (default: false)
- `auth_username` (str, optional): Username for HTTP authentication
- `auth_token` (str, optional): Token for HTTP authentication

**Example:**
```json
{
  "test_script": "git/git_operations.py",
  "test_function": "git_push_file",
  "authentication": {
    "authentication_type": "basic",
    "authentication_name": "github_test_private_repo"
  },
  "parameters": {
    "repo_dir": "<tmp>/test_private_repo",
    "file_path": "test_file.txt",
    "commit_message": "Add test file for automation testing",
    "clear_git_configs": true
  }
}
```

### git_delete_file
Removes a file from a Git repository and pushes the deletion with support for authentication and Git configuration management.

**Parameters:**
- `repo_dir` (str, required): Path to the Git repository
- `file_path` (str, required): Path to the file to remove
- `commit_message` (str, required): Commit message for the operation
- `clear_git_configs` (bool, optional): Clear Git configuration environment variables (default: false)
- `auth_username` (str, optional): Username for HTTP authentication
- `auth_token` (str, optional): Token for HTTP authentication

**Example:**
```json
{
  "test_script": "git/git_operations.py",
  "test_function": "git_delete_file",
  "authentication": {
    "authentication_type": "basic",
    "authentication_name": "github_test_private_repo"
  },
  "parameters": {
    "repo_dir": "<tmp>/test_private_repo",
    "file_path": "test_file.txt",
    "commit_message": "Remove test file after automation testing",
    "clear_git_configs": true
  }
}
```

## Authentication Setup

### GitHub Personal Access Token (PAT)

1. **Create a GitHub PAT:**
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token with appropriate permissions (repo scope for private repositories)
   - Copy the generated token

2. **Store Credentials:**
   ```bash
   python -c "
   from libs.credential_library import get_credential_manager
   cm = get_credential_manager()
   cm.store_credentials('github_test_private_repo', 'basic', username='your_username', password='your_token')
   "
   ```

3. **Test Plan Configuration:**
   ```json
   "authentication": {
     "authentication_type": "basic",
     "authentication_name": "github_test_private_repo"
   }
   ```

## Git Configuration Management

### clear_git_configs Parameter

The `clear_git_configs` parameter provides isolated Git testing by temporarily unsetting Git configuration environment variables:

- **GIT_CONFIG_GLOBAL**: Global Git configuration
- **GIT_CONFIG_SYSTEM**: System Git configuration

**Benefits:**
- Prevents interference from existing Git configurations
- Ensures consistent test environment
- Supports testing with different authentication methods

## Test Plan Integration

### Complete Git Workflow Example

```json
{
  "id": 5,
  "name": "Git Repository Operations Test",
  "description": "Test Git repository operations including clone, push, and delete operations with authentication",
  "steps": [
    {
      "step_number": 1,
      "test_script": "git/git_operations.py",
      "test_function": "git_clone",
      "authentication": {
        "authentication_type": "basic",
        "authentication_name": "github_test_private_repo"
      },
      "parameters": {
        "repo_url": "https://github.com/ThibaultLeveau/test_private_repo.git",
        "target_dir": "<tmp>/test_private_repo",
        "clear_git_configs": true
      }
    },
    {
      "step_number": 2,
      "test_script": "files/create_file.py",
      "test_function": "create_file",
      "parameters": {
        "file_path": "<tmp>/test_private_repo/test_file.txt",
        "content": "This is a test file created for Git operations testing",
        "ensure_parent_dirs": true
      }
    },
    {
      "step_number": 3,
      "test_script": "git/git_operations.py",
      "test_function": "git_push_file",
      "authentication": {
        "authentication_type": "basic",
        "authentication_name": "github_test_private_repo"
      },
      "parameters": {
        "repo_dir": "<tmp>/test_private_repo",
        "file_path": "test_file.txt",
        "commit_message": "Add test file for automation testing",
        "clear_git_configs": true
      }
    },
    {
      "step_number": 4,
      "test_script": "git/git_operations.py",
      "test_function": "git_delete_file",
      "authentication": {
        "authentication_type": "basic",
        "authentication_name": "github_test_private_repo"
      },
      "parameters": {
        "repo_dir": "<tmp>/test_private_repo",
        "file_path": "test_file.txt",
        "commit_message": "Remove test file after automation testing",
        "clear_git_configs": true
      }
    }
  ]
}
```

## Platform Support

- **Windows**: Full support with PowerShell Git commands
- **Linux**: Full support with bash Git commands
- **Cross-platform**: Compatible with both operating systems

## Error Handling

All Git functions return standardized result structures:

```python
{
  "stdout": "Standard output from the operation",
  "stderr": "Error output if any",
  "exception": "Exception message if any",
  "returncode": 0  # 0 for success, non-zero for failure
}
```

### Return Codes
- **0**: Test passed successfully
- **1**: Test failed (expected failure condition)
- **2**: Execution error (unexpected failure)
- **3**: Function import/loading error
- **4**: Parameter validation error

## Best Practices

1. **Use Temporary Directories**: Always use `<tmp>` tags for repository operations to ensure clean test environments
2. **Enable Git Config Clearing**: Set `clear_git_configs: true` for isolated testing
3. **Secure Authentication**: Use the credential library for secure token storage
4. **Meaningful Commit Messages**: Use descriptive commit messages for test traceability
5. **Error Handling**: Check return codes and handle errors appropriately in test plans

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Verify GitHub PAT has correct permissions
   - Check credential storage with credential library
   - Ensure repository URL is correct

2. **Repository Access Issues**:
   - Verify repository exists and is accessible
   - Check network connectivity
   - Ensure PAT has appropriate repository access

3. **Git Command Failures**:
   - Verify Git is installed and in PATH
   - Check Git version compatibility
   - Review stderr output for detailed error messages

### Debug Mode

Enable debug logging by setting environment variable:
```bash
set TEST_AUTOMATION_DEBUG=true
```

This provides detailed output for troubleshooting Git operations.
