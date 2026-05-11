"""
pytest Configuration and Fixtures
==================================

Shared test fixtures for the bookstore application.
"""

import os
import pytest
from uuid import uuid4
from decimal import Decimal

# Set testing environment
os.environ['FLASK_ENV'] = 'testing'

from app import create_app
from app.extensions import db as _db
from app.models import (
    User, Customer, Address, Book, Warehouse, Inventory,
    Invoice, InvoiceLine, BookRequest, Manufacturer, PurchaseOrder, POLine
)


# =============================================================================
# Application Fixtures
# =============================================================================

@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    """Create database tables."""
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """Create isolated database session for each test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    yield db.session
    
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


# =============================================================================
# User Fixtures
# =============================================================================

@pytest.fixture
def admin_user(session) -> User:
    """Create admin user."""
    user = User(
        email='admin@test.com',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    user.set_password('AdminPass123!')
    session.add(user)
    session.flush()
    return user


@pytest.fixture
def employee_user(session) -> User:
    """Create employee user."""
    user = User(
        email='employee@test.com',
        first_name='Employee',
        last_name='User',
        role='employee'
    )
    user.set_password('EmployeePass123!')
    session.add(user)
    session.flush()
    return user


@pytest.fixture
def customer_user(session) -> User:
    """Create customer user."""
    user = User(
        email='customer@test.com',
        first_name='Customer',
        last_name='User',
        role='customer'
    )
    user.set_password('CustomerPass123!')
    session.add(user)
    session.flush()
    return user


# =============================================================================
# Customer Fixtures
# =============================================================================

@pytest.fixture
def customer(session, customer_user) -> Customer:
    """Create customer with profile."""
    customer = Customer(
        user_id=customer_user.id,
        company_name='Test Company',
        phone='555-1234',
        credit_terms='Net 30'
    )
    session.add(customer)
    session.flush()
    return customer


@pytest.fixture
def customer_address(session, customer) -> Address:
    """Create customer address."""
    address = Address(
        customer_id=customer.id,
        address_type='billing',
        street='123 Test St',
        city='Test City',
        state='TS',
        zip_code='12345',
        country='USA',
        is_primary=True
    )
    session.add(address)
    session.flush()
    return address


# =============================================================================
# Book Fixtures
# =============================================================================

@pytest.fixture
def sample_book(session) -> Book:
    """Create sample book."""
    book = Book(
        isbn='978-0-13-235088-4',
        title='Clean Code',
        author='Robert C. Martin',
        publisher='Prentice Hall',
        year_published=2008,
        category='Programming'
    )
    session.add(book)
    session.flush()
    return book


@pytest.fixture
def multiple_books(session) -> list:
    """Create multiple books."""
    books_data = [
        {'title': 'Clean Code', 'author': 'Robert Martin', 'category': 'Programming'},
        {'title': 'Design Patterns', 'author': 'Gang of Four', 'category': 'Programming'},
        {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'category': 'Fiction'},
        {'title': 'Rare First Edition', 'author': 'Unknown', 'category': 'Rare'},
    ]
    
    books = []
    for data in books_data:
        book = Book(**data)
        session.add(book)
        books.append(book)
    
    session.flush()
    return books


# =============================================================================
# Inventory Fixtures
# =============================================================================

@pytest.fixture
def warehouse(session) -> Warehouse:
    """Create warehouse."""
    warehouse = Warehouse(
        name='Main Warehouse',
        location='123 Storage Lane',
        capacity=10000
    )
    session.add(warehouse)
    session.flush()
    return warehouse


@pytest.fixture
def inventory(session, sample_book, warehouse) -> Inventory:
    """Create inventory item."""
    inventory = Inventory(
        book_id=sample_book.id,
        warehouse_id=warehouse.id,
        condition=4,
        quantity=5,
        acquisition_cost=Decimal('25.00'),
        list_price=Decimal('49.99'),
        reorder_level=2,
        location_code='A1-S3'
    )
    session.add(inventory)
    session.flush()
    return inventory


# =============================================================================
# Invoice Fixtures
# =============================================================================

@pytest.fixture
def invoice(session, customer, admin_user) -> Invoice:
    """Create draft invoice."""
    invoice = Invoice(
        invoice_number='INV-20260101-0001',
        customer_id=customer.id,
        created_by=admin_user.id,
        status='draft',
        payment_terms='Net 30'
    )
    session.add(invoice)
    session.flush()
    return invoice


# =============================================================================
# Book Request Fixtures
# =============================================================================

@pytest.fixture
def book_request(session, customer) -> BookRequest:
    """Create book request."""
    request = BookRequest(
        customer_id=customer.id,
        title='Rare Programming Book',
        author='Famous Author',
        min_condition=3,
        max_price=Decimal('100.00')
    )
    session.add(request)
    session.flush()
    return request


# =============================================================================
# Purchase Order Fixtures
# =============================================================================

@pytest.fixture
def manufacturer(session) -> Manufacturer:
    """Create manufacturer."""
    manufacturer = Manufacturer(
        name='Test Publisher',
        contact_name='John Contact',
        email='contact@publisher.com',
        phone='555-9999'
    )
    session.add(manufacturer)
    session.flush()
    return manufacturer


@pytest.fixture
def purchase_order(session, manufacturer, admin_user) -> PurchaseOrder:
    """Create purchase order."""
    po = PurchaseOrder(
        po_number='PO-20260101-0001',
        manufacturer_id=manufacturer.id,
        created_by=admin_user.id,
        status='draft'
    )
    session.add(po)
    session.flush()
    return po


# =============================================================================
# Service Fixtures
# =============================================================================

@pytest.fixture
def user_service():
    """Get UserService instance."""
    from app.services import UserService
    return UserService()


@pytest.fixture
def customer_service():
    """Get CustomerService instance."""
    from app.services import CustomerService
    return CustomerService()


@pytest.fixture
def book_service():
    """Get BookService instance."""
    from app.services import BookService
    return BookService()


@pytest.fixture
def inventory_service():
    """Get InventoryService instance."""
    from app.services import InventoryService
    return InventoryService()


@pytest.fixture
def invoice_service():
    """Get InvoiceService instance."""
    from app.services import InvoiceService
    return InvoiceService()


@pytest.fixture
def book_request_service():
    """Get BookRequestService instance."""
    from app.services import BookRequestService
    return BookRequestService()


@pytest.fixture
def purchase_order_service():
    """Get PurchaseOrderService instance."""
    from app.services import PurchaseOrderService
    return PurchaseOrderService()
