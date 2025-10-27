#!/usr/bin/env python3
"""
Test Automation Library
Core functions for test plan processing and execution.
"""

import os
import json
import importlib.util
import glob
import sys
from datetime import datetime
from libs.log_library import create_log_manager, create_json_execution_logger
from libs.tmp_area_library import get_tmp_manager, create_tmp_area, cleanup_tmp_area, process_parameters
from libs.credential_library import resolve_authentication


class TestAutomationFramework:
    def __init__(self, test_plans_dir="test_plans", scripts_dir="scripts", debug_level=0, test_case_id=None):
        """
        Initialize the test automation framework.
        
        Args:
            test_plans_dir (str): Directory containing test plan JSON files
            scripts_dir (str): Directory containing test script Python files
            debug_level (int): Debug level (0=no debug, 1=debug on fail, 2=debug always)
            test_case_id (int): Optional test case ID to filter execution
        """
        self.test_plans_dir = test_plans_dir
        self.scripts_dir = scripts_dir
        self.debug_level = debug_level
        self.test_case_id = test_case_id
        self.results = []
        self.log_manager = create_log_manager(debug_level)
    
    def load_test_plan(self, plan_path):
        """Load and validate a test plan JSON file."""
        try:
            with open(plan_path, 'r') as f:
                plan = json.load(f)
            
            # Validate required fields
            required_fields = ['name', 'test_cases']
            for field in required_fields:
                if field not in plan:
                    raise ValueError(f"Missing required field: {field}")
            
            return plan
        except Exception as e:
            print(f"Error loading test plan {plan_path}: {e}")
            return None
    
    def import_test_function(self, script_path, function_name):
        """Dynamically import a test function from a script."""
        try:
            # Convert relative path to absolute
            if not script_path.startswith('/'):
                script_path = os.path.join(self.scripts_dir, script_path.lstrip('/'))
            
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Script not found: {script_path}")
            
            # Import the module
            spec = importlib.util.spec_from_file_location("test_module", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the function
            if hasattr(module, function_name):
                return getattr(module, function_name)
            else:
                raise AttributeError(f"Function '{function_name}' not found in {script_path}")
                
        except Exception as e:
            print(f"Error importing function {function_name} from {script_path}: {e}")
            return None
    
    def execute_test_step(self, step, test_case_name, is_negative_test=False):
        """Execute a single test step."""
        step_result = {
            "test_case": test_case_name,
            "step_number": step.get("step_number", "unknown"),
            "test_script": step.get("test_script", "unknown"),
            "test_function": step.get("test_function", "unknown"),
            "parameters": step.get("parameters", {}),
            "authentication": step.get("authentication", {}),
            "timestamp": datetime.now().isoformat(),
            "is_negative_test": is_negative_test,
            "result": {}
        }
        
        try:
            # Import and execute the test function
            test_function = self.import_test_function(
                step["test_script"], 
                step["test_function"]
            )
            
            if test_function:
                # Process parameters to resolve <tmp> tags
                processed_parameters = process_parameters(step["parameters"])
                
                # Resolve authentication if specified
                auth_config = step.get("authentication", {})
                if auth_config:
                    auth_credentials = resolve_authentication(auth_config)
                    if auth_credentials:
                        # Merge authentication credentials with parameters
                        processed_parameters.update(auth_credentials)
                        if self.debug_level >= 1:
                            print(f"Authentication resolved for step {step['step_number']}: {list(auth_credentials.keys())}")
                
                # Execute the function with processed parameters
                result = test_function(**processed_parameters)
                
                # Invert returncode for negative tests
                if is_negative_test:
                    original_returncode = result.get("returncode", 1)
                    result["returncode"] = 0 if original_returncode != 0 else 1
                    result["original_returncode"] = original_returncode
                    result["is_negative_test"] = True
                
                step_result["result"] = result
                
                # Add parameter processing info to result for debugging
                if self.debug_level >= 2:
                    step_result["processed_parameters"] = processed_parameters
                    step_result["original_parameters"] = step["parameters"]
                    if auth_config:
                        step_result["authentication_resolved"] = list(auth_credentials.keys())
                
            else:
                step_result["result"] = {
                    "stdout": "",
                    "stderr": f"Failed to import function {step['test_function']}",
                    "exception": "Function import failed",
                    "returncode": 3
                }
                
        except Exception as e:
            step_result["result"] = {
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exception": str(e),
                "returncode": 4
            }
        
        # Use log manager to display result
        self.log_manager.display_step_result(
            step["step_number"], 
            step_result["result"],
            test_case_name,
            is_negative_test
        )
        
        return step_result
    
    def execute_test_case(self, test_case, plan_name):
        """Execute all steps in a test case."""
        # Use log manager to display test case start
        self.log_manager.display_test_case_start(test_case)
        
        case_results = []
        
        # Check if this is a negative test
        is_negative_test = test_case.get("negative_test", False)
        
        for step in test_case.get("steps", []):
            step_result = self.execute_test_step(step, test_case["name"], is_negative_test)
            case_results.append(step_result)
        
        return case_results
    
    def execute_test_plan(self, plan_path):
        """Execute all test cases in a test plan."""
        plan = self.load_test_plan(plan_path)
        if not plan:
            return
        
        # Initialize JSON execution logger
        json_logger = create_json_execution_logger()
        command_line = " ".join(sys.argv)
        json_logger.start_execution(plan["name"], plan_path, command_line)
        
        # Create temporary area for this test plan execution
        tmp_result = create_tmp_area()
        if tmp_result["returncode"] != 0:
            print(f"Warning: Failed to create temporary area: {tmp_result.get('stderr', 'Unknown error')}")
        
        # Use log manager to display test plan start
        self.log_manager.display_test_plan_start(plan)
        
        plan_results = {
            "plan_name": plan["name"],
            "plan_path": plan_path,
            "timestamp": datetime.now().isoformat(),
            "tmp_area_info": {
                "tmp_path": get_tmp_manager().get_tmp_path() if get_tmp_manager().tmp_framework_path else None,
                "creation_result": tmp_result
            },
            "test_cases": []
        }
        
        # Filter test cases if test_case_id is specified
        test_cases_to_execute = plan["test_cases"]
        if self.test_case_id is not None:
            test_cases_to_execute = [
                tc for tc in plan["test_cases"] 
                if tc.get("id") == self.test_case_id
            ]
            
            if not test_cases_to_execute:
                print(f"Warning: Test case ID {self.test_case_id} not found in test plan")
                # Clean up temporary area before returning
                cleanup_tmp_area()
                return plan_results
        
        for test_case in test_cases_to_execute:
            case_results = self.execute_test_case(test_case, plan["name"])
            plan_results["test_cases"].extend(case_results)
            
            # Add step results to JSON logger
            for step_result in case_results:
                json_logger.add_step_result(step_result)
        
        # Generate summary
        total_steps = len(plan_results["test_cases"])
        passed_steps = sum(1 for step in plan_results["test_cases"] 
                          if step["result"].get("returncode", 1) == 0)
        
        # Use log manager to display summary
        self.log_manager.display_test_plan_summary(plan["name"], total_steps, passed_steps)
        
        # Save JSON execution log
        log_file_path = json_logger.finish_execution()
        if log_file_path:
            print(f"Execution log saved to: {log_file_path}")
        
        # Clean up temporary area after test plan execution
        cleanup_result = cleanup_tmp_area()
        if cleanup_result["returncode"] != 0:
            print(f"Warning: Failed to clean up temporary area: {cleanup_result.get('stderr', 'Unknown error')}")
        
        self.results.append(plan_results)
        return plan_results
    
    def run_all_test_plans(self):
        """Scan and execute all test plans in the test_plans directory."""
        print("Test Automation Framework - Starting Execution")
        print(f"Scanning directory: {self.test_plans_dir}")
        
        # Find all JSON files in test_plans directory
        pattern = os.path.join(self.test_plans_dir, "*.json")
        test_plan_files = glob.glob(pattern)
        
        if not test_plan_files:
            print("No test plan files found in test_plans directory")
            return
        
        print(f"Found {len(test_plan_files)} test plan(s)")
        
        for plan_file in test_plan_files:
            self.execute_test_plan(plan_file)
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate a final execution report."""
        # Use log manager to display final report
        self.log_manager.display_final_report(self.results)
        
        # Save detailed results to file
        report_file = f"test_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)


def validate_test_plan_structure(test_plan):
    """
    Validate the structure of a test plan dictionary.
    
    Args:
        test_plan (dict): Test plan dictionary to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['name', 'test_cases']
    
    for field in required_fields:
        if field not in test_plan:
            return False, f"Missing required field: {field}"
    
    if not isinstance(test_plan['test_cases'], list):
        return False, "test_cases must be a list"
    
    for i, test_case in enumerate(test_plan['test_cases']):
        case_required = ['id', 'name', 'description', 'steps']
        for field in case_required:
            if field not in test_case:
                return False, f"Test case {i} missing required field: {field}"
        
        if not isinstance(test_case['steps'], list):
            return False, f"Test case {i} steps must be a list"
        
        for j, step in enumerate(test_case['steps']):
            step_required = ['step_number', 'test_script', 'test_function', 'parameters']
            for field in step_required:
                if field not in step:
                    return False, f"Step {j} in test case {i} missing required field: {field}"
    
    return True, "Test plan structure is valid"


def scan_test_plans_directory(directory="test_plans"):
    """
    Scan a directory for test plan JSON files.
    
    Args:
        directory (str): Directory to scan
        
    Returns:
        list: List of test plan file paths
    """
    pattern = os.path.join(directory, "*.json")
    return glob.glob(pattern)


def create_test_execution_report(results, output_file=None):
    """
    Create a test execution report from results.
    
    Args:
        results (list): List of test execution results
        output_file (str, optional): Output file path
        
    Returns:
        dict: Report data
    """
    if output_file is None:
        output_file = f"test_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_plans": len(results),
            "total_steps": sum(len(plan["test_cases"]) for plan in results),
            "total_passed": sum(
                sum(1 for step in plan["test_cases"] if step["result"].get("returncode", 1) == 0)
                for plan in results
            )
        },
        "detailed_results": results
    }
    
    # Calculate success rate
    total_steps = report["summary"]["total_steps"]
    if total_steps > 0:
        report["summary"]["success_rate"] = (report["summary"]["total_passed"] / total_steps) * 100
    else:
        report["summary"]["success_rate"] = 0
    
    report["summary"]["total_failed"] = total_steps - report["summary"]["total_passed"]
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report
