#!/usr/bin/env python3
"""
Log Library
Handles debug level management and result display for the test automation framework.
"""

import json
import uuid
import time
import getpass
import os
from datetime import datetime


class LogManager:
    def __init__(self, debug_level=0):
        """
        Initialize the log manager with debug level.
        
        Args:
            debug_level (int): Debug level (0=no debug, 1=debug on fail, 2=debug always)
        """
        self.debug_level = debug_level
    
    def should_show_debug(self, step_result):
        """
        Determine if debug output should be shown for a step based on debug level and result.
        
        Args:
            step_result (dict): Step execution result
            
        Returns:
            bool: True if debug output should be shown, False otherwise
        """
        if self.debug_level == 0:
            return False
        elif self.debug_level == 1:
            # Show debug only for failed steps
            return step_result.get("returncode", 1) != 0
        elif self.debug_level == 2:
            # Show debug for all steps
            return True
        return False
    
    def display_step_result(self, step_number, step_result, test_case_name="", is_negative_test=False):
        """
        Display step execution result based on debug level.
        
        Args:
            step_number (str/int): Step number identifier
            step_result (dict): Step execution result
            test_case_name (str): Optional test case name for context
            is_negative_test (bool): Whether this is a negative test (inverted logic)
        """
        # Determine status based on negative test logic
        if is_negative_test:
            # For negative tests: PASS when returncode != 0, FAIL when returncode == 0
            status = "PASSED" if step_result.get("returncode", 0) != 0 else "FAILED"
            status_indicator = " [NEGATIVE]"
        else:
            # For normal tests: PASS when returncode == 0, FAIL when returncode != 0
            status = "PASSED" if step_result.get("returncode", 1) == 0 else "FAILED"
            status_indicator = ""
        
        # Basic status display (always shown)
        context = f" ({test_case_name})" if test_case_name else ""
        print(f"  Step {step_number}{context}: {status}{status_indicator}")
        
        # Debug output based on debug level
        if self.should_show_debug(step_result):
            self._display_debug_output(step_result, is_negative_test)
    
    def _display_debug_output(self, step_result, is_negative_test=False):
        """
        Display detailed debug output for a step.
        
        Args:
            step_result (dict): Step execution result
            is_negative_test (bool): Whether this is a negative test
        """
        indent = "    "
        
        # Always show STDOUT, even if empty
        stdout = step_result.get("stdout", "").strip()
        print(f"{indent}STDOUT: {stdout if stdout else '(empty)'}")
        
        # Always show STDERR, even if empty
        stderr = step_result.get("stderr", "").strip()
        print(f"{indent}STDERR: {stderr if stderr else '(empty)'}")
        
        # Always show EXCEPTION, even if empty
        exception = step_result.get("exception", "").strip()
        print(f"{indent}EXCEPTION: {exception if exception else '(empty)'}")
        
        # Show return code with additional info for negative tests
        returncode = step_result.get("returncode", 1)
        if is_negative_test and "original_returncode" in step_result:
            original_returncode = step_result.get("original_returncode", 1)
            print(f"{indent}RETURNCODE: {returncode} (inverted from {original_returncode} for negative test)")
        else:
            print(f"{indent}RETURNCODE: {returncode}")
    
    def display_test_case_start(self, test_case):
        """
        Display test case execution start information.
        
        Args:
            test_case (dict): Test case information
        """
        print(f"\nExecuting Test Case: {test_case['name']}")
        print(f"Description: {test_case.get('description', 'No description')}")
    
    def display_test_plan_start(self, plan):
        """
        Display test plan execution start information.
        
        Args:
            plan (dict): Test plan information
        """
        from datetime import datetime
        
        print(f"\n{'='*60}")
        print(f"Executing Test Plan: {plan['name']}")
        print(f"Description: {plan.get('description', 'No description')}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"{'='*60}")
    
    def display_test_plan_summary(self, plan_name, total_steps, passed_steps):
        """
        Display test plan execution summary.
        
        Args:
            plan_name (str): Test plan name
            total_steps (int): Total number of steps executed
            passed_steps (int): Number of steps that passed
        """
        print(f"\n{'='*60}")
        print(f"Test Plan Summary: {plan_name}")
        print(f"Total Steps: {total_steps}")
        print(f"Passed: {passed_steps}")
        print(f"Failed: {total_steps - passed_steps}")
        
        if total_steps > 0:
            success_rate = (passed_steps / total_steps) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        else:
            print("Success Rate: N/A")
        
        print(f"{'='*60}")
    
    def display_final_report(self, results):
        """
        Display final execution report.
        
        Args:
            results (list): List of test execution results
        """
        from datetime import datetime
        
        print(f"\n{'#'*80}")
        print("# FINAL EXECUTION REPORT")
        print(f"{'#'*80}")
        
        total_plans = len(results)
        total_steps = sum(len(plan["test_cases"]) for plan in results)
        total_passed = sum(
            sum(1 for step in plan["test_cases"] if step["result"].get("returncode", 1) == 0)
            for plan in results
        )
        
        print(f"Total Test Plans Executed: {total_plans}")
        print(f"Total Test Steps Executed: {total_steps}")
        print(f"Total Steps Passed: {total_passed}")
        print(f"Total Steps Failed: {total_steps - total_passed}")
        
        if total_steps > 0:
            success_rate = (total_passed / total_steps) * 100
            print(f"Overall Success Rate: {success_rate:.1f}%")
        
        print(f"{'#'*80}")
        
        # Report file information
        report_file = f"test_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        print(f"Detailed report saved to: {report_file}")


def create_log_manager(debug_level=0):
    """
    Factory function to create a LogManager instance.
    
    Args:
        debug_level (int): Debug level (0=no debug, 1=debug on fail, 2=debug always)
        
    Returns:
        LogManager: Configured log manager instance
    """
    return LogManager(debug_level)


class JSONExecutionLogger:
    """
    Handles JSON logging for test executions
    
    Creates individual JSON log files for each test plan execution
    in the test_execution_log/ directory.
    """
    
    def __init__(self):
        """Initialize the JSON execution logger."""
        self.log_dir = "test_execution_log"
        self.execution_start_time = None
        self.current_execution_data = None
        
    def start_execution(self, plan_name, plan_file, command_line):
        """
        Start tracking a new test execution.
        
        Args:
            plan_name (str): Name of the test plan
            plan_file (str): Path to the test plan file
            command_line (str): Command line used to execute
        """
        self.execution_start_time = time.perf_counter()
        self.current_execution_data = {
            "execution_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "current_user": getpass.getuser(),
            "test_plan": plan_file,
            "test_plan_name": plan_name,
            "command_line": command_line,
            "execution_time_seconds": 0.0,
            "results": {
                "total_steps": 0,
                "passed_steps": 0,
                "failed_steps": 0,
                "success_rate": 0.0
            },
            "detailed_results": []
        }
    
    def add_step_result(self, step_result):
        """
        Add a step result to the current execution.
        
        Args:
            step_result (dict): Step execution result
        """
        if self.current_execution_data:
            # Update summary statistics
            self.current_execution_data["results"]["total_steps"] += 1
            if step_result["result"].get("returncode", 1) == 0:
                self.current_execution_data["results"]["passed_steps"] += 1
            else:
                self.current_execution_data["results"]["failed_steps"] += 1
            
            # Calculate success rate
            total_steps = self.current_execution_data["results"]["total_steps"]
            passed_steps = self.current_execution_data["results"]["passed_steps"]
            if total_steps > 0:
                self.current_execution_data["results"]["success_rate"] = (passed_steps / total_steps) * 100
            
            # Add detailed result with stdout, stderr, and exception
            detailed_result = {
                "test_case": step_result.get("test_case", "unknown"),
                "step_number": step_result.get("step_number", "unknown"),
                "status": "PASSED" if step_result["result"].get("returncode", 1) == 0 else "FAILED",
                "returncode": step_result["result"].get("returncode", 1),
                "timestamp": step_result.get("timestamp", datetime.now().isoformat()),
                "stdout": step_result["result"].get("stdout", ""),
                "stderr": step_result["result"].get("stderr", ""),
                "exception": step_result["result"].get("exception", "")
            }
            self.current_execution_data["detailed_results"].append(detailed_result)
    
    def finish_execution(self):
        """
        Finish the current execution and save to JSON file.
        
        Returns:
            str: Path to the saved log file
        """
        if not self.current_execution_data:
            return None
        
        # Calculate execution time
        if self.execution_start_time:
            execution_time = time.perf_counter() - self.execution_start_time
            self.current_execution_data["execution_time_seconds"] = round(execution_time, 2)
        
        # Ensure log directory exists
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Generate filename
        plan_name_clean = self._clean_filename(self.current_execution_data["test_plan_name"])
        timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M")
        filename = f"log_{plan_name_clean}_{timestamp}.json"
        filepath = os.path.join(self.log_dir, filename)
        
        # Save to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.current_execution_data, f, indent=2, ensure_ascii=False)
            return filepath
        except Exception as e:
            print(f"Error saving execution log: {e}")
            return None
    
    def _clean_filename(self, filename):
        """
        Clean a string to be safe for use as a filename.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Cleaned filename
        """
        # Replace problematic characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove multiple consecutive underscores
        while '__' in filename:
            filename = filename.replace('__', '_')
        
        # Remove leading/trailing underscores and spaces
        filename = filename.strip(' _')
        
        # Limit length to avoid filesystem issues
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename


def create_json_execution_logger():
    """
    Factory function to create a JSONExecutionLogger instance.
    
    Returns:
        JSONExecutionLogger: Configured JSON execution logger instance
    """
    return JSONExecutionLogger()
