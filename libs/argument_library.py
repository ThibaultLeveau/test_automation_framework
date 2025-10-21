#!/usr/bin/env python3
"""
Argument Library
Handles command-line argument parsing and validation for the test automation framework.
"""

import argparse
import sys
import os


def parse_arguments():
    """
    Parse command-line arguments for the test automation framework.
    
    Returns:
        argparse.Namespace: Parsed arguments with the following attributes:
            - test_plan (str): Path to test plan JSON file
            - test_case_id (int): Optional test case ID to filter execution
            - debug_level (int): Debug level (0=no debug, 1=debug on fail, 2=debug always)
    """
    parser = argparse.ArgumentParser(
        description="Test Automation Framework - Execute test plans with filtering and debugging options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  main.py test_plan.json                    # Execute all test cases in plan
  main.py test_plan.json -i 1              # Execute only test case with ID 1
  main.py test_plan.json -d 1              # Debug output for failed steps only
  main.py test_plan.json -i 1 -d 2         # Execute ID 1 with full debug output
  main.py -h                               # Show this help message

Debug Levels:
  0 (default): No debug - only basic pass/fail status
  1: Debug on fail - show STDOUT, STDERR, EXCEPTION for failed steps
  2: Debug always - show STDOUT, STDERR, EXCEPTION for all steps
        """
    )
    
    # Required positional argument
    parser.add_argument(
        'test_plan',
        nargs='?',  # Make it optional to support -h without arguments
        help='Path to test plan JSON file (optional if using -h)'
    )
    
    # Optional arguments
    parser.add_argument(
        '-i', '--test-case-id',
        type=int,
        metavar='ID',
        help='Filter execution to specific test case ID'
    )
    
    parser.add_argument(
        '-d', '--debug-level',
        type=int,
        choices=[0, 1, 2],
        default=0,
        metavar='LEVEL',
        help='Debug output level (0=no debug, 1=debug on fail, 2=debug always)'
    )
    
    return parser.parse_args()


def validate_arguments(args):
    """
    Validate parsed command-line arguments.
    
    Args:
        args (argparse.Namespace): Parsed arguments
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # If help was requested, no further validation needed
    if len(sys.argv) == 1 or '-h' in sys.argv or '--help' in sys.argv:
        return True, ""
    
    # Check if test_plan is provided when not using help
    if not args.test_plan:
        return False, "Error: test_plan argument is required (use -h for help)"
    
    # Check if test plan file exists
    if not os.path.exists(args.test_plan):
        return False, f"Error: Test plan file not found: {args.test_plan}"
    
    # Check if test plan file is a JSON file
    if not args.test_plan.lower().endswith('.json'):
        return False, f"Error: Test plan must be a JSON file: {args.test_plan}"
    
    return True, ""


def get_arguments():
    """
    Main function to get and validate command-line arguments.
    
    Returns:
        tuple: (args, error_message) - args is None if validation fails
    """
    try:
        args = parse_arguments()
        is_valid, error_message = validate_arguments(args)
        
        if not is_valid:
            return None, error_message
        
        return args, ""
        
    except SystemExit:
        # argparse calls sys.exit() when -h is used
        return None, "help_requested"
    except Exception as e:
        return None, f"Error parsing arguments: {str(e)}"
