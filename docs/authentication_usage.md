# Authentication Usage Guide

## Overview

The test automation framework now supports secure credential management using OS keyring services. This allows you to store authentication credentials securely instead of including them in plain text in test plans.

## Authentication Structure

### Test Step Authentication Section

Add an optional `authentication` section to your test steps:

```json
{
  "step_number": 1,
  "test_script": "http/http_request.py",
  "test_function": "make_http_request",
  "authentication": {
    "authentication_type": "basic",
    "authentication_name": "my_service_auth"
  },
  "parameters": {
    "url": "https://api.example.com/secure-endpoint",
    "method": "GET",
    "expected_status": 200
  }
}
```

### Authentication Configuration Fields

- **authentication_type** (required): Type of authentication
  - `basic`: Username/password authentication
  - `token`: Bearer token authentication
  
- **authentication_name** (required): Unique identifier for these credentials
  - Used to store/retrieve credentials from OS keyring
  - Format: `test_automation_framework_{auth_name}`

## How It Works

### First-Time Execution
1. When a test step with authentication is executed for the first time
2. The framework detects no stored credentials
3. User is prompted to enter credentials interactively
4. Credentials are securely stored in OS keyring
5. Test execution continues with the provided credentials

### Subsequent Executions
1. Framework checks OS keyring for existing credentials
2. If found, credentials are automatically retrieved
3. No user interaction required
4. Test executes with stored credentials

## Supported Authentication Types

### Basic Authentication
- Stores username and password
- Used for HTTP Basic Auth, API keys, etc.
- Parameters injected: `auth_username`, `auth_password`, `auth_type`

### Token Authentication
- Stores bearer/API tokens
- Used for JWT tokens, OAuth tokens, etc.
- Parameters injected: `auth_token`, `auth_type`

## Script Integration

### Standardized Authentication Parameters

Script functions should accept these standardized parameters:

```python
def my_function(param1, param2, auth_username=None, auth_password=None, auth_token=None, auth_type=None):
    # Function implementation
    pass
```

### Backward Compatibility

Existing scripts continue to work with legacy parameters:
- `username`, `password`, `bearer_token`

New standardized parameters take priority over legacy parameters.

## Credential Management

### Manual Credential Management

You can manage credentials manually using the credential library:

```bash
# Store credentials
python libs/credential_library.py --auth-name my_service --auth-type basic --action store

# Retrieve credentials (metadata only)
python libs/credential_library.py --auth-name my_service --auth-type basic --action retrieve

# Delete credentials
python libs/credential_library.py --auth-name my_service --auth-type basic --action delete
```

### OS Keyring Integration

- **Windows**: Uses Windows Credential Manager
- **Linux**: Uses system keyring (GNOME Keyring, KWallet, etc.)
- **macOS**: Uses macOS Keychain

Credentials are stored under service name: `test_automation_framework_{auth_name}`

## Example Test Plans

### Basic Authentication Example

```json
{
  "id": 1,
  "name": "API Authentication Test",
  "description": "Test API with basic authentication",
  "steps": [
    {
      "step_number": 1,
      "test_script": "http/http_request.py",
      "test_function": "make_http_request",
      "authentication": {
        "authentication_type": "basic",
        "authentication_name": "my_api_auth"
      },
      "parameters": {
        "url": "https://api.example.com/data",
        "method": "GET",
        "expected_status": 200
      }
    }
  ]
}
```

### Token Authentication Example

```json
{
  "id": 2,
  "name": "JWT Token Test",
  "description": "Test API with JWT token authentication",
  "steps": [
    {
      "step_number": 1,
      "test_script": "http/http_request.py",
      "test_function": "make_http_request",
      "authentication": {
        "authentication_type": "token",
        "authentication_name": "jwt_token_auth"
      },
      "parameters": {
        "url": "https://api.example.com/protected",
        "method": "GET",
        "expected_status": 200
      }
    }
  ]
}
```

## Security Benefits

- **No Plain Text Credentials**: Credentials are never stored in test plan files
- **OS-Level Security**: Uses platform-native secure storage
- **User Control**: Users manage their own credentials
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Backward Compatible**: Existing test plans continue to work

## Troubleshooting

### Credential Not Found
- Ensure authentication_name is consistent across test executions
- Check if credentials were stored successfully
- Verify OS keyring service is available

### Permission Issues
- Ensure user has permission to access keyring
- On Linux, may require keyring daemon to be running

### Migration from Legacy Authentication
1. Remove `username`, `password`, `bearer_token` from parameters
2. Add `authentication` section with appropriate type and name
3. Run test once to store credentials
4. Subsequent runs will use stored credentials automatically

## Best Practices

1. **Use Descriptive Names**: Choose meaningful authentication_name values
2. **Environment-Specific Credentials**: Use different auth names for different environments
3. **Regular Cleanup**: Remove unused credentials from keyring
4. **Team Coordination**: Coordinate auth names when working in teams
5. **Documentation**: Document authentication requirements in test plan descriptions
