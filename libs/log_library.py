#!/usr/bin/env python3
"""
Log Library
Handles debug level management and result display for the test automation framework.
"""


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
    
    def display_step_result(self, step_number, step_result, test_case_name=""):
        """
        Display step execution result based on debug level.
        
        Args:
            step_number (str/int): Step number identifier
            step_result (dict): Step execution result
            test_case_name (str): Optional test case name for context
        """
        status = "PASSED" if step_result.get("returncode", 1) == 0 else "FAILED"
        
        # Basic status display (always shown)
        context = f" ({test_case_name})" if test_case_name else ""
        print(f"  Step {step_number}{context}: {status}")
        
        # Debug output based on debug level
        if self.should_show_debug(step_result):
            self._display_debug_output(step_result)
    
    def _display_debug_output(self, step_result):
        """
        Display detailed debug output for a step.
        
        Args:
            step_result (dict): Step execution result
        """
        indent = "    "
        
        # Show STDOUT if present
        stdout = step_result.get("stdout", "").strip()
        if stdout:
            print(f"{indent}STDOUT: {stdout}")
        
        # Show STDERR if present
        stderr = step_result.get("stderr", "").strip()
        if stderr:
            print(f"{indent}STDERR: {stderr}")
        
        # Show EXCEPTION if present
        exception = step_result.get("exception", "").strip()
        if exception:
            print(f"{indent}EXCEPTION: {exception}")
        
        # Show return code
        returncode = step_result.get("returncode", 1)
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
