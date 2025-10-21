#!/usr/bin/env python3
"""
Test Automation Framework - Main Execution Engine
This script scans test plans in the test_plans directory and executes the referenced test functions.
"""

import os
import sys
from libs.test_library import TestAutomationFramework

def main():
    """Main entry point for the test automation framework."""
    framework = TestAutomationFramework()
    
    # Check for specific test plan argument
    if len(sys.argv) > 1:
        plan_path = sys.argv[1]
        if os.path.exists(plan_path):
            framework.execute_test_plan(plan_path)
        else:
            print(f"Test plan not found: {plan_path}")
    else:
        # Execute all test plans
        framework.run_all_test_plans()

if __name__ == "__main__":
    main()
