"""
pytest configuration and shared fixtures.

This file is automatically loaded by pytest and provides fixtures
available to all tests in the test suite.

Test Categories:
- unit/: Isolated unit tests (no database)
- integration/: Tests requiring database
- fixtures/: Test data files (JSON, etc.)
"""

import os
import pytest
from typing import Generator

# Set testing environment before importing app
os.environ['FLASK_ENV'] = 'testing'

from app import create_app
from app.extensions import db as _db
from app.models import User, Customer, Book, Inventory, Warehouse


# =============================================================================
# Application Fixtures
# =============================================================================

@pytest.fixture(scope='session')
def app():
    """
    Create application instance for the test session.
    
    Scope: session - created once, shared across all tests.
    """
    app = create_app('testing')
    
    # Establish application context
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    """
    Create database tables for the test session.
    
    Scope: session - tables created once, persisted across tests.
    Individual tests should use transactions for isolation.
    """
    _db.create_all()
    
    yield _db
    
    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """
    Create a new database session for each test.
    
    Scope: function - new session per test, rolled back after.
    Provides test isolation without recreating tables.
    """
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Bind session to this connection
    session = db.session
    
    yield session
    
    # Rollback transaction (undo all changes)
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(app):
    """
    Create a test client for making HTTP requests.
    
    Usage:
        def test_home(client):
            response = client.get('/')
            assert response.status_code == 200
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Create a CLI test runner for testing Flask commands.
    
    Usage:
        def test_cli(runner):
            result = runner.invoke(some_command)
            assert result.exit_code == 0
    """
    return app.test_cli_runner()


# =============================================================================
# Authentication Fixtures
# =============================================================================

@pytest.fixture
def admin_user(session) -> User:
    """Create an admin user for testing."""
    user = User(
        email='admin@test.com',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    user.set_password('AdminPass123!')
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def employee_user(session) -> User:
    """Create an employee user for testing."""
    user = User(
        email='employee@test.com',
        first_name='Employee',
        last_name='User',
        role='employee'
    )
    user.set_password('EmployeePass123!')
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def customer_user(session) -> User:
    """Create a customer user for testing."""
    user = User(
        email='customer@test.com',
        first_name='Customer',
        last_name='User',
        role='customer'
    )
    user.set_password('CustomerPass123!')
    session.add(user)
    session.commit()
    
    # Create associated customer profile
    customer = Customer(
        user_id=user.id,
        phone='555-1234',
        credit_terms='Net 30'
    )
    session.add(customer)
    session.commit()
    
    return user


@pytest.fixture
def authenticated_client(client, admin_user):
    """
    Create a test client with an authenticated admin session.
    
    Usage:
        def test_protected_route(authenticated_client):
            response = authenticated_client.get('/admin/dashboard')
            assert response.status_code == 200
    """
    with client.session_transaction() as sess:
        sess['user_id'] = str(admin_user.id)
        sess['_fresh'] = True
    return client


# =============================================================================
# Data Fixtures
# =============================================================================

@pytest.fixture
def sample_warehouse(session) -> Warehouse:
    """Create a sample warehouse for testing."""
    warehouse = Warehouse(
        name='Main Warehouse',
        location='123 Storage Lane',
        capacity=10000
    )
    session.add(warehouse)
    session.commit()
    return warehouse


@pytest.fixture
def sample_book(session) -> Book:
    """Create a sample book for testing."""
    book = Book(
        isbn='978-0-13-235088-4',
        title='Clean Code',
        author='Robert C. Martin',
        publisher='Prentice Hall',
        year_published=2008,
        category='Programming'
    )
    session.add(book)
    session.commit()
    return book


@pytest.fixture
def sample_inventory(session, sample_book, sample_warehouse) -> Inventory:
    """Create sample inventory for testing."""
    inventory = Inventory(
        book_id=sample_book.id,
        warehouse_id=sample_warehouse.id,
        condition=4,  # Very Good
        quantity=5,
        acquisition_cost=25.00,
        list_price=49.99,
        location_code='A1-S3'
    )
    session.add(inventory)
    session.commit()
    return inventory


@pytest.fixture
def multiple_books(session) -> list:
    """Create multiple books for testing lists/search."""
    books_data = [
        {
            'isbn': '978-0-13-235088-4',
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'category': 'Programming'
        },
        {
            'isbn': '978-0-201-63361-0',
            'title': 'Design Patterns',
            'author': 'Gang of Four',
            'category': 'Programming'
        },
        {
            'isbn': '978-0-06-112008-4',
            'title': 'To Kill a Mockingbird',
            'author': 'Harper Lee',
            'category': 'Fiction'
        },
        {
            'title': 'Rare First Edition',
            'author': 'Unknown Author',
            'year_published': 1850,
            'category': 'Rare'
        },
    ]
    
    books = []
    for data in books_data:
        book = Book(**data)
        session.add(book)
        books.append(book)
    
    session.commit()
    return books


# =============================================================================
# Helper Fixtures
# =============================================================================

@pytest.fixture
def auth_headers(admin_user) -> dict:
    """
    Generate authorization headers for API requests.
    
    Note: This is a placeholder for JWT implementation.
    Will be updated when authentication is implemented.
    """
    # TODO: Generate actual JWT token
    return {
        'Authorization': f'Bearer test-token-{admin_user.id}'
    }


# =============================================================================
# Cleanup Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def cleanup_uploads(app):
    """
    Clean up any uploaded files after each test.
    
    autouse=True means this runs automatically for every test.
    """
    yield
    
    # Cleanup code runs after test
    upload_path = os.path.join(app.instance_path, 'uploads')
    if os.path.exists(upload_path):
        import shutil
        shutil.rmtree(upload_path)


# =============================================================================
# Marks and Configuration
# =============================================================================

def pytest_configure(config):
    """
    Configure custom pytest markers.
    
    Usage in tests:
        @pytest.mark.slow
        def test_slow_operation():
            ...
    
    Run only fast tests: pytest -m "not slow"
    """
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "security: marks security-related tests")
