#!/usr/bin/env python3
"""
Temporary Area Management Library
Handles creation, management, and cleanup of temporary directories for test automation.
"""

import os
import platform
import tempfile
import shutil
import json
from datetime import datetime


class TmpAreaManager:
    """Manages temporary directory operations for the test automation framework."""
    
    def __init__(self):
        """Initialize the temporary area manager."""
        self.tmp_base_path = None
        self.tmp_framework_path = None
        self.execution_id = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from global.json."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'global.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            self.linux_tmp_path = config['tmp']['linux_tmp_path']
            self.windows_tmp_path = config['tmp']['windows_tmp_path']
            
        except Exception as e:
            # Fallback configuration
            self.linux_tmp_path = "/tmp/test_automation_framework"
            self.windows_tmp_path = "C:/test_automation_framework"
            print(f"Warning: Could not load config, using fallback: {e}")
    
    def get_platform_tmp_path(self):
        """
        Get the platform-specific temporary directory path.
        
        Returns:
            str: Platform-specific temporary directory path
        """
        try:
            # Use tempfile.gettempdir() for cross-platform compatibility
            base_tmp = tempfile.gettempdir()
            
            # For Windows, ensure we're using the system temp directory
            if platform.system() == "Windows":
                # Use environment variable as fallback
                base_tmp = os.environ.get('TEMP', base_tmp)
            
            return base_tmp
            
        except Exception as e:
            # Fallback to current directory if temp directory is unavailable
            print(f"Warning: Could not determine temp directory, using current directory: {e}")
            return os.getcwd()
    
    def create_tmp_area(self):
        """
        Create the temporary directory structure for the current execution.
        
        Returns:
            dict: Result structure with path information
        """
        result = {
            "stdout": "",
            "stderr": "",
            "exception": "",
            "returncode": 0
        }
        
        try:
            # Generate unique execution ID
            self.execution_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Get platform-specific base path from config
            if platform.system() == "Windows":
                base_tmp = self.windows_tmp_path
            else:
                base_tmp = self.linux_tmp_path
            
            # Create execution-specific directory
            self.tmp_framework_path = os.path.join(base_tmp, self.execution_id)
            os.makedirs(self.tmp_framework_path, exist_ok=True)
            
            result["stdout"] = f"Temporary area created: {self.tmp_framework_path}"
            result["returncode"] = 0
            
        except Exception as e:
            result["stderr"] = f"Failed to create temporary area: {str(e)}"
            result["exception"] = str(e)
            result["returncode"] = 2
        
        return result
    
    def cleanup_tmp_area(self):
        """
        Clean up the temporary directory structure.
        
        Returns:
            dict: Result structure with cleanup information
        """
        result = {
            "stdout": "",
            "stderr": "",
            "exception": "",
            "returncode": 0
        }
        
        try:
            if self.tmp_framework_path and os.path.exists(self.tmp_framework_path):
                # On Windows, we need to handle file permissions before deletion
                if platform.system() == "Windows":
                    self._fix_windows_permissions(self.tmp_framework_path)
                
                shutil.rmtree(self.tmp_framework_path)
                result["stdout"] = f"Temporary area cleaned up: {self.tmp_framework_path}"
                
        except Exception as e:
            result["stderr"] = f"Failed to clean up temporary area: {str(e)}"
            result["exception"] = str(e)
            result["returncode"] = 2
        
        return result
    
    def _fix_windows_permissions(self, path):
        """
        Fix file permissions on Windows to allow deletion.
        
        Args:
            path (str): Path to fix permissions for
        """
        if platform.system() != "Windows":
            return
            
        try:
            for root, dirs, files in os.walk(path):
                for name in files:
                    file_path = os.path.join(root, name)
                    try:
                        os.chmod(file_path, 0o666)  # Make file writable
                    except:
                        pass  # Ignore permission errors on individual files
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    try:
                        os.chmod(dir_path, 0o777)  # Make directory writable
                    except:
                        pass  # Ignore permission errors on individual directories
        except:
            pass  # Ignore any errors in the permission fixing process
    
    def resolve_tmp_path(self, path_with_tag):
        """
        Replace <tmp> tags in paths with the actual temporary directory path.
        
        Args:
            path_with_tag (str): Path containing <tmp> tag
            
        Returns:
            str: Resolved path with actual temporary directory
        """
        if not self.tmp_framework_path:
            raise ValueError("Temporary area not created. Call create_tmp_area() first.")
        
        if isinstance(path_with_tag, str) and "<tmp>" in path_with_tag:
            # Replace <tmp> tag with the actual temporary directory path
            resolved_path = path_with_tag.replace("<tmp>", self.tmp_framework_path)
            
            # Normalize path separators for the current platform
            resolved_path = os.path.normpath(resolved_path)
            
            return resolved_path
        
        return path_with_tag
    
    def process_parameters(self, parameters):
        """
        Process parameters dictionary and resolve all <tmp> tags.
        
        Args:
            parameters (dict): Dictionary of parameters to process
            
        Returns:
            dict: Parameters with resolved tmp paths
        """
        if not isinstance(parameters, dict):
            return parameters
        
        processed_params = {}
        
        for key, value in parameters.items():
            if isinstance(value, str):
                processed_params[key] = self.resolve_tmp_path(value)
            elif isinstance(value, dict):
                processed_params[key] = self.process_parameters(value)
            elif isinstance(value, list):
                processed_params[key] = [self.process_parameters(item) if isinstance(item, dict) 
                                       else self.resolve_tmp_path(item) if isinstance(item, str) 
                                       else item for item in value]
            else:
                processed_params[key] = value
        
        return processed_params
    
    def get_tmp_path(self):
        """
        Get the current temporary directory path.
        
        Returns:
            str: Current temporary directory path
        """
        if not self.tmp_framework_path:
            raise ValueError("Temporary area not created. Call create_tmp_area() first.")
        
        return self.tmp_framework_path
    
    def create_subdirectory(self, subdir_name):
        """
        Create a subdirectory within the temporary area.
        
        Args:
            subdir_name (str): Name of the subdirectory to create
            
        Returns:
            dict: Result structure with creation information
        """
        result = {
            "stdout": "",
            "stderr": "",
            "exception": "",
            "returncode": 0
        }
        
        try:
            if not self.tmp_framework_path:
                raise ValueError("Temporary area not created. Call create_tmp_area() first.")
            
            subdir_path = os.path.join(self.tmp_framework_path, subdir_name)
            os.makedirs(subdir_path, exist_ok=True)
            
            result["stdout"] = f"Subdirectory created: {subdir_path}"
            result["returncode"] = 0
            
        except Exception as e:
            result["stderr"] = f"Failed to create subdirectory: {str(e)}"
            result["exception"] = str(e)
            result["returncode"] = 2
        
        return result


# Global instance for easy access
_tmp_manager = None


def get_tmp_manager():
    """
    Get or create the global temporary area manager instance.
    
    Returns:
        TmpAreaManager: Global temporary area manager instance
    """
    global _tmp_manager
    if _tmp_manager is None:
        _tmp_manager = TmpAreaManager()
    return _tmp_manager


def create_tmp_area():
    """Create the temporary area using the global manager."""
    return get_tmp_manager().create_tmp_area()


def cleanup_tmp_area():
    """Clean up the temporary area using the global manager."""
    return get_tmp_manager().cleanup_tmp_area()


def resolve_tmp_path(path_with_tag):
    """Resolve <tmp> tags in paths using the global manager."""
    return get_tmp_manager().resolve_tmp_path(path_with_tag)


def process_parameters(parameters):
    """Process parameters and resolve <tmp> tags using the global manager."""
    return get_tmp_manager().process_parameters(parameters)


def get_tmp_path():
    """Get the current temporary directory path using the global manager."""
    return get_tmp_manager().get_tmp_path()


def create_subdirectory(subdir_name):
    """Create a subdirectory within the temporary area using the global manager."""
    return get_tmp_manager().create_subdirectory(subdir_name)


# Test function for direct execution
if __name__ == "__main__":
    # Test the tmp area functionality
    print("Testing TmpAreaManager...")
    
    manager = TmpAreaManager()
    
    # Test creation
    result = manager.create_tmp_area()
    print(f"Create result: {result}")
    
    # Test path resolution
    test_path = manager.resolve_tmp_path("<tmp>/test_file.txt")
    print(f"Resolved path: {test_path}")
    
    # Test parameter processing
    test_params = {
        "file_path": "<tmp>/data.txt",
        "config": {
            "input_dir": "<tmp>/input",
            "output_dir": "<tmp>/output"
        },
        "files": ["<tmp>/file1.txt", "<tmp>/file2.txt"]
    }
    processed = manager.process_parameters(test_params)
    print(f"Processed params: {processed}")
    
    # Test cleanup
    result = manager.cleanup_tmp_area()
    print(f"Cleanup result: {result}")
