"""
API Endpoint Integration Tests
==============================

Task: QA-S2-001

Tests for all REST API endpoints.

Run with: pytest tests/integration/test_api_endpoints.py -v
From the bookstore/ directory.
"""

import os
import sys
import pytest
import json
from uuid import uuid4
from decimal import Decimal

# Add parent directory to path for standalone execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app
from app.extensions import db
from app.models import User, Book, Warehouse, Inventory, Customer, Invoice, Manufacturer, PurchaseOrder


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client, app):
    """Get authentication headers for admin user."""
    with app.app_context():
        # Create admin user
        admin = User(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        admin.set_password('password123')
        db.session.add(admin)
        db.session.commit()
    
    # Login to get token
    response = client.post('/api/v1/auth/login', 
        data=json.dumps({'email': 'admin@test.com', 'password': 'password123'}),
        content_type='application/json'
    )
    data = json.loads(response.data)
    token = data['data']['access_token']
    
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


@pytest.fixture
def sample_book(app):
    """Create a sample book."""
    with app.app_context():
        book = Book(
            title='Test Book',
            author='Test Author',
            isbn='978-0-13-235088-4',
            category='Testing'
        )
        db.session.add(book)
        db.session.commit()
        return str(book.id)


@pytest.fixture
def sample_warehouse(app):
    """Create a sample warehouse."""
    with app.app_context():
        warehouse = Warehouse(
            name='Test Warehouse',
            location='123 Test St',
            capacity=1000
        )
        db.session.add(warehouse)
        db.session.commit()
        return str(warehouse.id)


class TestAuthAPI:
    """Test authentication endpoints."""
    
    def test_register(self, client):
        """Test user registration."""
        response = client.post('/api/v1/auth/register',
            data=json.dumps({
                'email': 'newuser@test.com',
                'password': 'password123',
                'first_name': 'New',
                'last_name': 'User'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['user']['email'] == 'newuser@test.com'
    
    def test_login(self, client, app):
        """Test user login."""
        # Create user first
        with app.app_context():
            user = User(
                email='login@test.com',
                first_name='Login',
                last_name='Test',
                role='customer'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/api/v1/auth/login',
            data=json.dumps({
                'email': 'login@test.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'access_token' in data['data']
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/v1/auth/login',
            data=json.dumps({
                'email': 'wrong@test.com',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_protected_route_without_token(self, client):
        """Test accessing protected route without token."""
        response = client.get('/api/v1/auth/me')
        assert response.status_code == 401


class TestBooksAPI:
    """Test book endpoints."""
    
    def test_list_books(self, client):
        """Test listing books (public endpoint)."""
        response = client.get('/api/v1/books')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'pagination' in data
    
    def test_create_book(self, client, auth_headers):
        """Test creating a book."""
        response = client.post('/api/v1/books',
            data=json.dumps({
                'title': 'New Book',
                'author': 'New Author',
                'category': 'Fiction'
            }),
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['title'] == 'New Book'
    
    def test_create_book_unauthorized(self, client):
        """Test creating book without auth."""
        response = client.post('/api/v1/books',
            data=json.dumps({
                'title': 'New Book',
                'author': 'New Author'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_get_book(self, client, sample_book):
        """Test getting a single book."""
        response = client.get(f'/api/v1/books/{sample_book}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['title'] == 'Test Book'
    
    def test_get_categories(self, client, sample_book):
        """Test getting categories."""
        response = client.get('/api/v1/books/categories')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestInventoryAPI:
    """Test inventory endpoints."""
    
    def test_list_inventory(self, client):
        """Test listing inventory (public)."""
        response = client.get('/api/v1/inventory')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_add_inventory(self, client, auth_headers, sample_book, sample_warehouse):
        """Test adding inventory."""
        response = client.post('/api/v1/inventory',
            data=json.dumps({
                'book_id': sample_book,
                'warehouse_id': sample_warehouse,
                'condition': 4,
                'quantity': 10,
                'acquisition_cost': '25.00',
                'list_price': '49.99'
            }),
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['quantity'] == 10
    
    def test_get_warehouses(self, client, sample_warehouse):
        """Test getting warehouses."""
        response = client.get('/api/v1/warehouses')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestInvoicesAPI:
    """Test invoice endpoints."""
    
    def test_list_invoices_requires_auth(self, client):
        """Test that listing invoices requires authentication."""
        response = client.get('/api/v1/invoices')
        assert response.status_code == 401
    
    def test_list_invoices(self, client, auth_headers):
        """Test listing invoices."""
        response = client.get('/api/v1/invoices', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestPurchaseOrdersAPI:
    """Test purchase order endpoints."""
    
    def test_list_pos_requires_auth(self, client):
        """Test that listing POs requires authentication."""
        response = client.get('/api/v1/purchase-orders')
        assert response.status_code == 401
    
    def test_list_pos(self, client, auth_headers):
        """Test listing purchase orders."""
        response = client.get('/api/v1/purchase-orders', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestCustomersAPI:
    """Test customer endpoints."""
    
    def test_create_customer(self, client):
        """Test customer registration."""
        response = client.post('/api/v1/customers',
            data=json.dumps({
                'email': 'customer@test.com',
                'password': 'password123',
                'first_name': 'Customer',
                'last_name': 'Test'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['email'] == 'customer@test.com'


class TestUsersAPI:
    """Test user management endpoints."""
    
    def test_list_users_requires_admin(self, client, app):
        """Test that listing users requires admin role."""
        # Create employee user
        with app.app_context():
            employee = User(
                email='employee@test.com',
                first_name='Employee',
                last_name='User',
                role='employee'
            )
            employee.set_password('password123')
            db.session.add(employee)
            db.session.commit()
        
        # Login as employee
        response = client.post('/api/v1/auth/login',
            data=json.dumps({'email': 'employee@test.com', 'password': 'password123'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        token = data['data']['access_token']
        
        # Try to list users
        response = client.get('/api/v1/users',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 403
    
    def test_list_users_as_admin(self, client, auth_headers):
        """Test listing users as admin."""
        response = client.get('/api/v1/users', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
