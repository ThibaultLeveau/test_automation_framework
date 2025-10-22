#!/usr/bin/env python3
"""
Credential Library
Secure credential storage and retrieval using OS keyring services.
Provides cross-platform credential management for test automation framework.
"""

import os
import sys
import keyring
import getpass
from typing import Dict, Optional, Tuple

# Service name prefix for credential storage
CREDENTIAL_SERVICE_PREFIX = "test_automation_framework"

class CredentialManager:
    """
    Manages secure credential storage and retrieval using OS keyring.
    """
    
    def __init__(self):
        """Initialize the credential manager."""
        self.service_prefix = CREDENTIAL_SERVICE_PREFIX
    
    def get_service_name(self, auth_name: str) -> str:
        """
        Generate the service name for credential storage.
        
        Args:
            auth_name (str): Authentication name identifier
            
        Returns:
            str: Full service name for keyring
        """
        return f"{self.service_prefix}_{auth_name}"
    
    def get_credentials(self, auth_name: str, auth_type: str) -> Dict[str, str]:
        """
        Retrieve credentials from OS keyring.
        
        Args:
            auth_name (str): Authentication name identifier
            auth_type (str): Authentication type ('basic' or 'token')
            
        Returns:
            dict: Credentials dictionary with keys based on auth_type
        """
        service_name = self.get_service_name(auth_name)
        credentials = {}
        
        try:
            if auth_type == "basic":
                # For basic auth, retrieve username and password
                username = keyring.get_password(service_name, "username")
                password = keyring.get_password(service_name, "password")
                
                if username and password:
                    credentials = {
                        "auth_username": username,
                        "auth_password": password,
                        "auth_type": "basic"
                    }
                    
            elif auth_type == "token":
                # For token auth, retrieve token
                token = keyring.get_password(service_name, "token")
                
                if token:
                    credentials = {
                        "auth_token": token,
                        "auth_type": "token"
                    }
                    
        except Exception as e:
            print(f"Warning: Failed to retrieve credentials for {auth_name}: {e}")
            
        return credentials
    
    def store_credentials(self, auth_name: str, auth_type: str, 
                         username: Optional[str] = None, 
                         password: Optional[str] = None,
                         token: Optional[str] = None) -> bool:
        """
        Store credentials in OS keyring.
        
        Args:
            auth_name (str): Authentication name identifier
            auth_type (str): Authentication type ('basic' or 'token')
            username (str, optional): Username for basic auth
            password (str, optional): Password for basic auth
            token (str, optional): Token for token auth
            
        Returns:
            bool: True if storage was successful, False otherwise
        """
        service_name = self.get_service_name(auth_name)
        
        try:
            if auth_type == "basic":
                if username and password:
                    keyring.set_password(service_name, "username", username)
                    keyring.set_password(service_name, "password", password)
                    return True
                else:
                    print("Error: Username and password are required for basic authentication")
                    return False
                    
            elif auth_type == "token":
                if token:
                    keyring.set_password(service_name, "token", token)
                    return True
                else:
                    print("Error: Token is required for token authentication")
                    return False
                    
            else:
                print(f"Error: Unsupported authentication type: {auth_type}")
                return False
                
        except Exception as e:
            print(f"Error: Failed to store credentials for {auth_name}: {e}")
            return False
    
    def prompt_for_credentials(self, auth_name: str, auth_type: str) -> Dict[str, str]:
        """
        Prompt user for credentials and store them securely.
        
        Args:
            auth_name (str): Authentication name identifier
            auth_type (str): Authentication type ('basic' or 'token')
            
        Returns:
            dict: Credentials dictionary with standardized keys
        """
        print(f"\nAuthentication required for: {auth_name}")
        print(f"Authentication type: {auth_type}")
        
        credentials = {}
        
        try:
            if auth_type == "basic":
                username = input("Username: ")
                password = getpass.getpass("Password: ")
                
                if self.store_credentials(auth_name, auth_type, username, password):
                    credentials = {
                        "auth_username": username,
                        "auth_password": password,
                        "auth_type": "basic"
                    }
                    print(f"Credentials stored securely for {auth_name}")
                else:
                    print(f"Failed to store credentials for {auth_name}")
                    
            elif auth_type == "token":
                token = getpass.getpass("Token: ")
                
                if self.store_credentials(auth_name, auth_type, token=token):
                    credentials = {
                        "auth_token": token,
                        "auth_type": "token"
                    }
                    print(f"Token stored securely for {auth_name}")
                else:
                    print(f"Failed to store token for {auth_name}")
                    
            else:
                print(f"Unsupported authentication type: {auth_type}")
                
        except KeyboardInterrupt:
            print("\nCredential input cancelled")
        except Exception as e:
            print(f"Error during credential input: {e}")
            
        return credentials
    
    def delete_credentials(self, auth_name: str) -> bool:
        """
        Delete credentials from OS keyring.
        
        Args:
            auth_name (str): Authentication name identifier
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        service_name = self.get_service_name(auth_name)
        
        try:
            # Delete username and password for basic auth
            keyring.delete_password(service_name, "username")
            keyring.delete_password(service_name, "password")
            
            # Delete token for token auth
            keyring.delete_password(service_name, "token")
            
            return True
            
        except keyring.errors.PasswordDeleteError:
            # This is normal if credentials don't exist
            return True
        except Exception as e:
            print(f"Error deleting credentials for {auth_name}: {e}")
            return False
    
    def credential_exists(self, auth_name: str, auth_type: str) -> bool:
        """
        Check if credentials exist for the given authentication name.
        
        Args:
            auth_name (str): Authentication name identifier
            auth_type (str): Authentication type ('basic' or 'token')
            
        Returns:
            bool: True if credentials exist, False otherwise
        """
        service_name = self.get_service_name(auth_name)
        
        try:
            if auth_type == "basic":
                username = keyring.get_password(service_name, "username")
                password = keyring.get_password(service_name, "password")
                return bool(username and password)
                
            elif auth_type == "token":
                token = keyring.get_password(service_name, "token")
                return bool(token)
                
            else:
                return False
                
        except Exception:
            return False


# Global credential manager instance
_credential_manager = None

def get_credential_manager() -> CredentialManager:
    """
    Get the global credential manager instance.
    
    Returns:
        CredentialManager: Global credential manager instance
    """
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = CredentialManager()
    return _credential_manager

def resolve_authentication(auth_config: Dict) -> Dict[str, str]:
    """
    Resolve authentication credentials from configuration.
    
    Args:
        auth_config (dict): Authentication configuration from test step
        
    Returns:
        dict: Authentication parameters for test function
    """
    if not auth_config:
        return {}
        
    auth_type = auth_config.get("authentication_type")
    auth_name = auth_config.get("authentication_name")
    
    if not auth_type or not auth_name:
        return {}
    
    credential_manager = get_credential_manager()
    
    # Try to get existing credentials
    credentials = credential_manager.get_credentials(auth_name, auth_type)
    
    # If credentials don't exist, prompt user
    if not credentials:
        credentials = credential_manager.prompt_for_credentials(auth_name, auth_type)
    
    return credentials


# Test function for direct execution
if __name__ == "__main__":
    # Simple test of credential functionality
    import argparse
    
    parser = argparse.ArgumentParser(description="Credential Library Test")
    parser.add_argument("--auth-name", required=True, help="Authentication name")
    parser.add_argument("--auth-type", choices=["basic", "token"], required=True, help="Authentication type")
    parser.add_argument("--action", choices=["store", "retrieve", "delete"], required=True, help="Action to perform")
    
    args = parser.parse_args()
    
    cm = get_credential_manager()
    
    if args.action == "store":
        if args.auth_type == "basic":
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            success = cm.store_credentials(args.auth_name, args.auth_type, username, password)
            print(f"Store {'successful' if success else 'failed'}")
        else:
            token = getpass.getpass("Token: ")
            success = cm.store_credentials(args.auth_name, args.auth_type, token=token)
            print(f"Store {'successful' if success else 'failed'}")
            
    elif args.action == "retrieve":
        credentials = cm.get_credentials(args.auth_name, args.auth_type)
        if credentials:
            print(f"Credentials found: {list(credentials.keys())}")
            # Don't print actual credentials for security
        else:
            print("No credentials found")
            
    elif args.action == "delete":
        success = cm.delete_credentials(args.auth_name)
        print(f"Delete {'successful' if success else 'failed'}")
