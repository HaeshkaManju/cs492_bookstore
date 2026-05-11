"""
Test Suite
==========

This package contains all tests for the Bookstore application.

Structure:
    tests/
    ├── conftest.py      - Shared pytest fixtures
    ├── unit/            - Unit tests (isolated, fast)
    │   ├── test_models.py
    │   ├── test_services.py
    │   └── test_utils.py
    ├── integration/     - Integration tests (database, routes)
    │   ├── test_auth.py
    │   ├── test_inventory.py
    │   └── test_customer_flow.py
    └── fixtures/        - Test data and factories

Running tests:
    pytest                    # All tests
    pytest tests/unit         # Unit tests only
    pytest -v                 # Verbose output
    pytest --cov=app          # With coverage report
    pytest -k "test_user"     # Tests matching pattern
"""
