#!/usr/bin/env python3
"""
HTTP: Generic HTTP request function
This script provides a comprehensive HTTP request function supporting multiple authentication types,
custom headers, request body, proxy configuration, and SSL certificate verification.
"""

import os
import sys
import json
import requests
from requests.auth import HTTPBasicAuth

def make_http_request(url, method="GET", auth_type="none", username=None, password=None, 
                     bearer_token=None, custom_auth_header=None, headers=None, body=None,
                     proxy_server=None, proxy_auth=None, ca_cert=None, verify_ssl=True,
                     timeout=30, expected_status=200):
    """
    Execute an HTTP request with comprehensive configuration options.
    
    Args:
        url (str): Target URL for the HTTP request (required)
        method (str): HTTP method (GET, POST, PUT, DELETE, etc.) (default: GET)
        auth_type (str): Authentication type - "none", "basic", "bearer", "custom" (default: "none")
        username (str): Username for basic authentication
        password (str): Password for basic authentication
        bearer_token (str): Bearer token for bearer authentication
        custom_auth_header (dict): Custom authentication headers
        headers (dict): Additional request headers
        body (dict/str): Request body for POST/PUT requests
        proxy_server (str): Proxy server URL
        proxy_auth (dict): Proxy authentication credentials
        ca_cert (str): Path to CA certificate file
        verify_ssl (bool): Enable SSL certificate verification (default: True)
        timeout (int): Request timeout in seconds (default: 30)
        expected_status (int/list): Expected HTTP status code(s) (default: 200)
        
    Returns:
        dict: Standardized result structure containing:
            - stdout (str): Standard output with response details
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
        if not url:
            result["stderr"] = "URL parameter is required"
            result["returncode"] = 4
            return result
        
        if not method:
            result["stderr"] = "HTTP method parameter is required"
            result["returncode"] = 4
            return result
        
        # Normalize method to uppercase
        method = method.upper()
        
        # Validate authentication parameters based on auth_type
        if auth_type == "basic" and (not username or not password):
            result["stderr"] = "Username and password are required for basic authentication"
            result["returncode"] = 4
            return result
        
        if auth_type == "bearer" and not bearer_token:
            result["stderr"] = "Bearer token is required for bearer authentication"
            result["returncode"] = 4
            return result
        
        if auth_type == "custom" and not custom_auth_header:
            result["stderr"] = "Custom authentication headers are required for custom authentication"
            result["returncode"] = 4
            return result
        
        # Prepare request parameters
        request_params = {
            'timeout': timeout,
            'verify': verify_ssl
        }
        
        # Handle SSL certificate verification
        if ca_cert and verify_ssl:
            if not os.path.exists(ca_cert):
                result["stderr"] = f"CA certificate file not found: {ca_cert}"
                result["returncode"] = 4
                return result
            request_params['verify'] = ca_cert
        
        # Handle authentication
        if auth_type == "basic":
            request_params['auth'] = HTTPBasicAuth(username, password)
        elif auth_type == "bearer":
            if not headers:
                headers = {}
            headers['Authorization'] = f'Bearer {bearer_token}'
        elif auth_type == "custom" and custom_auth_header:
            if not headers:
                headers = {}
            headers.update(custom_auth_header)
        
        # Handle headers
        if headers:
            request_params['headers'] = headers
        
        # Handle proxy configuration
        if proxy_server:
            request_params['proxies'] = {'http': proxy_server, 'https': proxy_server}
            if proxy_auth:
                request_params['proxies'] = {
                    'http': f"http://{proxy_auth.get('username', '')}:{proxy_auth.get('password', '')}@{proxy_server.replace('http://', '').replace('https://', '')}",
                    'https': f"https://{proxy_auth.get('username', '')}:{proxy_auth.get('password', '')}@{proxy_server.replace('http://', '').replace('https://', '')}"
                }
        
        # Handle request body
        if body and method in ['POST', 'PUT', 'PATCH']:
            if isinstance(body, dict):
                request_params['json'] = body
            else:
                request_params['data'] = body
        
        # Execute the HTTP request
        response = requests.request(method, url, **request_params)
        
        # Prepare response details
        response_details = {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'url': response.url,
            'elapsed': str(response.elapsed)
        }
        
        # Try to parse response content
        try:
            response_details['body'] = response.json()
        except:
            response_details['body'] = response.text
        
        # Check expected status
        expected_codes = [expected_status] if isinstance(expected_status, int) else expected_status
        if response.status_code not in expected_codes:
            result["stderr"] = f"Expected status {expected_codes}, got {response.status_code}"
            result["returncode"] = 1
            result["stdout"] = json.dumps(response_details, indent=2)
        else:
            result["stdout"] = json.dumps(response_details, indent=2)
            result["returncode"] = 0
        
    except requests.exceptions.Timeout:
        result["exception"] = f"Request timed out after {timeout} seconds"
        result["returncode"] = 2
    except requests.exceptions.ConnectionError as e:
        result["exception"] = f"Connection error: {str(e)}"
        result["returncode"] = 2
    except requests.exceptions.RequestException as e:
        result["exception"] = f"Request error: {str(e)}"
        result["returncode"] = 2
    except Exception as e:
        result["exception"] = str(e)
        result["returncode"] = 2
    
    return result

# Test function for direct execution
if __name__ == "__main__":
    # Parse command line arguments for testing
    if len(sys.argv) > 1:
        url = sys.argv[1]
        method = sys.argv[2] if len(sys.argv) > 2 else "GET"
        auth_type = sys.argv[3] if len(sys.argv) > 3 else "none"
        username = sys.argv[4] if len(sys.argv) > 4 else None
        password = sys.argv[5] if len(sys.argv) > 5 else None
        
        result = make_http_request(url, method, auth_type, username, password)
        print(result)
    else:
        # Example usage
        print("Usage: python http_request.py <url> [method] [auth_type] [username] [password]")
        print("Example: python http_request.py https://httpbin.org/basic-auth/user/password GET basic user password")
