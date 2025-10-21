#!/usr/bin/env python3
"""
Test Automation Library
Core functions for test plan processing and execution.
"""

import os
import json
import importlib.util
import glob
from datetime import datetime


class TestAutomationFramework:
    def __init__(self, test_plans_dir="test_plans", scripts_dir="scripts"):
        """
        Initialize the test automation framework.
        
        Args:
            test_plans_dir (str): Directory containing test plan JSON files
            scripts_dir (str): Directory containing test script Python files
        """
        self.test_plans_dir = test_plans_dir
        self.scripts_dir = scripts_dir
        self.results = []
    
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
    
    def execute_test_step(self, step, test_case_name):
        """Execute a single test step."""
        step_result = {
            "test_case": test_case_name,
            "step_number": step.get("step_number", "unknown"),
            "test_script": step.get("test_script", "unknown"),
            "test_function": step.get("test_function", "unknown"),
            "parameters": step.get("parameters", {}),
            "timestamp": datetime.now().isoformat(),
            "result": {}
        }
        
        try:
            # Import and execute the test function
            test_function = self.import_test_function(
                step["test_script"], 
                step["test_function"]
            )
            
            if test_function:
                # Execute the function with parameters
                result = test_function(**step["parameters"])
                step_result["result"] = result
                
                # Print execution result
                status = "PASSED" if result.get("returncode", 1) == 0 else "FAILED"
                print(f"  Step {step['step_number']}: {status} - {result.get('stdout', result.get('stderr', 'No output'))}")
                
            else:
                step_result["result"] = {
                    "stdout": "",
                    "stderr": f"Failed to import function {step['test_function']}",
                    "exception": "Function import failed",
                    "returncode": 3
                }
                print(f"  Step {step['step_number']}: FAILED - Function import failed")
                
        except Exception as e:
            step_result["result"] = {
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exception": str(e),
                "returncode": 4
            }
            print(f"  Step {step['step_number']}: FAILED - Execution error: {e}")
        
        return step_result
    
    def execute_test_case(self, test_case, plan_name):
        """Execute all steps in a test case."""
        print(f"\nExecuting Test Case: {test_case['name']}")
        print(f"Description: {test_case.get('description', 'No description')}")
        
        case_results = []
        
        for step in test_case.get("steps", []):
            step_result = self.execute_test_step(step, test_case["name"])
            case_results.append(step_result)
        
        return case_results
    
    def execute_test_plan(self, plan_path):
        """Execute all test cases in a test plan."""
        plan = self.load_test_plan(plan_path)
        if not plan:
            return
        
        print(f"\n{'='*60}")
        print(f"Executing Test Plan: {plan['name']}")
        print(f"Description: {plan.get('description', 'No description')}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"{'='*60}")
        
        plan_results = {
            "plan_name": plan["name"],
            "plan_path": plan_path,
            "timestamp": datetime.now().isoformat(),
            "test_cases": []
        }
        
        for test_case in plan["test_cases"]:
            case_results = self.execute_test_case(test_case, plan["name"])
            plan_results["test_cases"].extend(case_results)
        
        # Generate summary
        total_steps = len(plan_results["test_cases"])
        passed_steps = sum(1 for step in plan_results["test_cases"] 
                          if step["result"].get("returncode", 1) == 0)
        
        print(f"\n{'='*60}")
        print(f"Test Plan Summary: {plan['name']}")
        print(f"Total Steps: {total_steps}")
        print(f"Passed: {passed_steps}")
        print(f"Failed: {total_steps - passed_steps}")
        print(f"Success Rate: {(passed_steps/total_steps)*100:.1f}%" if total_steps > 0 else "N/A")
        print(f"{'='*60}")
        
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
        print(f"\n{'#'*80}")
        print("# FINAL EXECUTION REPORT")
        print(f"{'#'*80}")
        
        total_plans = len(self.results)
        total_steps = sum(len(plan["test_cases"]) for plan in self.results)
        total_passed = sum(
            sum(1 for step in plan["test_cases"] if step["result"].get("returncode", 1) == 0)
            for plan in self.results
        )
        
        print(f"Total Test Plans Executed: {total_plans}")
        print(f"Total Test Steps Executed: {total_steps}")
        print(f"Total Steps Passed: {total_passed}")
        print(f"Total Steps Failed: {total_steps - total_passed}")
        
        if total_steps > 0:
            success_rate = (total_passed / total_steps) * 100
            print(f"Overall Success Rate: {success_rate:.1f}%")
        
        print(f"{'#'*80}")
        
        # Save detailed results to file
        report_file = f"test_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Detailed report saved to: {report_file}")


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
