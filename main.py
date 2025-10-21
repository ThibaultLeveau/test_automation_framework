#!/usr/bin/env python3
"""
Test Automation Framework - Main Execution Engine
This script scans test plans in the test_plans directory and executes the referenced test functions.
"""

import os
import sys
from libs.test_library import TestAutomationFramework
from libs.argument_library import get_arguments

def main():
    """Main entry point for the test automation framework."""
    # Parse command-line arguments
    args, error_message = get_arguments()
    
    if error_message == "help_requested":
        # Help was displayed, exit normally
        return
    elif error_message:
        # Error occurred during argument parsing
        print(error_message)
        sys.exit(1)
    
    # Initialize framework with parsed arguments
    framework = TestAutomationFramework(
        debug_level=args.debug_level,
        test_case_id=args.test_case_id
    )
    
    # Execute the specified test plan
    if args.test_plan:
        framework.execute_test_plan(args.test_plan)
    else:
        print("Error: No test plan specified. Use -h for help.")
        sys.exit(1)

if __name__ == "__main__":
    main()
