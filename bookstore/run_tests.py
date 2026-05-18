#!/usr/bin/env python
"""
Test Runner Script
==================

Run all tests from the bookstore directory:
    python run_tests.py

Run specific test file:
    python run_tests.py tests/integration/test_api_endpoints.py

Run with verbose output:
    python run_tests.py -v
"""

import sys
import os

# Ensure we're in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

if __name__ == '__main__':
    import pytest
    
    # Default to running all tests if no arguments provided
    args = sys.argv[1:] if len(sys.argv) > 1 else ['tests/', '-v']
    
    sys.exit(pytest.main(args))
