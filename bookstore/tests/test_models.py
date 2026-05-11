"""
Model Tests
===========

Tests for SQLAlchemy models.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from uuid import UUID

from app.models import (
    User, Customer, Address, Book, Warehouse, Inventory,
    Invoice, InvoiceLine, BookRequest, Manufacturer, PurchaseOrder, POLine
)


class TestUserModel:
    """Tests for User model."""
    
    def test_create_user(self, session):
        """Test user creation."""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='customer'
        )
        user.set_password('SecurePass123!')
        session.add(user)
        session.flush()
        
        assert user.id is not None
        assert isinstance(user.id, UUID)
        assert user.email == 'test@example.com'
        assert user.is_active is True
    
    def test_password_hashing(self, session):
        """Test password is hashed, not stored plaintext."""
        user = User(email='pwd@test.com', first_name='Pwd', last_name='Test')
        user.set_password('MyPassword123!')
        
        assert user.password_hash != 'MyPassword123!'
        assert user.check_password('MyPassword123!') is True
        assert user.check_password('WrongPassword') is False
    
    def test_full_name(self, session):
        """Test full_name property."""
        user = User(
            email='name@test.com',
            first_name='John',
            last_name='Doe'
        )
        
        assert user.full_name == 'John Doe'
    
    def test_display_name_with_company(self, session):
        """Test display_name uses company if available."""
        user = User(
            email='company@test.com',
            first_name='Jane',
            last_name='Smith'
        )
        session.add(user)
        session.flush()
        
        customer = Customer(
            user_id=user.id,
            company_name='Smith Industries'
        )
        session.add(customer)
        session.flush()
        
        assert customer.display_name == 'Smith Industries'
    
    def test_timestamps(self, session):
        """Test created_at and updated_at are set."""
        user = User(email='time@test.com', first_name='Time', last_name='Test')
        session.add(user)
        session.flush()
        
        assert user.created_at is not None
        assert user.updated_at is not None


class TestBookModel:
    """Tests for Book model."""
    
    def test_create_book(self, session):
        """Test book creation."""
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
        
        assert book.id is not None
        assert book.is_active is True
    
    def test_book_without_isbn(self, session):
        """Test book can be created without ISBN."""
        book = Book(
            title='Unknown Rare Book',
            author='Unknown Author'
        )
        session.add(book)
        session.flush()
        
        assert book.id is not None
        assert book.isbn is None
    
    def test_to_dict(self, session):
        """Test to_dict method."""
        book = Book(
            title='Test Book',
            author='Test Author',
            category='Test'
        )
        session.add(book)
        session.flush()
        
        data = book.to_dict()
        
        assert 'id' in data
        assert data['title'] == 'Test Book'
        assert data['author'] == 'Test Author'


class TestInventoryModel:
    """Tests for Inventory model."""
    
    def test_create_inventory(self, sample_book, warehouse, session):
        """Test inventory creation."""
        inventory = Inventory(
            book_id=sample_book.id,
            warehouse_id=warehouse.id,
            condition=4,
            quantity=10,
            acquisition_cost=Decimal('25.00'),
            list_price=Decimal('49.99'),
            reorder_level=2
        )
        session.add(inventory)
        session.flush()
        
        assert inventory.id is not None
    
    def test_condition_label(self, inventory, session):
        """Test condition_label property."""
        inventory.condition = 1
        assert inventory.condition_label == 'Poor'
        
        inventory.condition = 3
        assert inventory.condition_label == 'Good'
        
        inventory.condition = 5
        assert inventory.condition_label == 'Fine'
    
    def test_is_low_stock(self, inventory, session):
        """Test is_low_stock property."""
        inventory.quantity = 5
        inventory.reorder_level = 2
        assert inventory.is_low_stock is False
        
        inventory.quantity = 1
        assert inventory.is_low_stock is True
    
    def test_profit_margin(self, inventory, session):
        """Test profit_margin calculation."""
        inventory.acquisition_cost = Decimal('50.00')
        inventory.list_price = Decimal('100.00')
        
        # Margin = (100 - 50) / 100 = 0.5 = 50%
        assert inventory.profit_margin == 50.0
    
    def test_adjust_quantity(self, inventory, session):
        """Test adjust_quantity method."""
        inventory.quantity = 10
        
        inventory.adjust_quantity(5)  # Add 5
        assert inventory.quantity == 15
        
        inventory.adjust_quantity(-3)  # Remove 3
        assert inventory.quantity == 12
    
    def test_adjust_quantity_negative_result(self, inventory, session):
        """Test adjust_quantity doesn't go below zero."""
        inventory.quantity = 5
        
        with pytest.raises(ValueError):
            inventory.adjust_quantity(-10)


class TestInvoiceModel:
    """Tests for Invoice model."""
    
    def test_create_invoice(self, customer, admin_user, session):
        """Test invoice creation."""
        invoice = Invoice(
            invoice_number='INV-TEST-001',
            customer_id=customer.id,
            created_by=admin_user.id,
            status='draft'
        )
        session.add(invoice)
        session.flush()
        
        assert invoice.id is not None
        assert invoice.status == 'draft'
    
    def test_invoice_subtotal(self, invoice, session):
        """Test subtotal calculation."""
        # Add lines
        line1 = InvoiceLine(
            invoice_id=invoice.id,
            description='Item 1',
            quantity=2,
            unit_price=Decimal('10.00')
        )
        line2 = InvoiceLine(
            invoice_id=invoice.id,
            description='Item 2',
            quantity=1,
            unit_price=Decimal('25.00')
        )
        session.add_all([line1, line2])
        session.flush()
        
        # Subtotal = (2 * 10) + (1 * 25) = 45
        assert invoice.subtotal == Decimal('45.00')
    
    def test_line_count(self, invoice, session):
        """Test line_count property."""
        assert invoice.line_count == 0
        
        line = InvoiceLine(
            invoice_id=invoice.id,
            description='Test',
            quantity=1,
            unit_price=Decimal('10.00')
        )
        session.add(line)
        session.flush()
        
        assert invoice.line_count == 1
    
    def test_line_total(self, invoice, session):
        """Test InvoiceLine total calculation."""
        line = InvoiceLine(
            invoice_id=invoice.id,
            description='Test Item',
            quantity=3,
            unit_price=Decimal('15.50')
        )
        session.add(line)
        session.flush()
        
        # Total = 3 * 15.50 = 46.50
        assert line.total == Decimal('46.50')


class TestBookRequestModel:
    """Tests for BookRequest model."""
    
    def test_create_request(self, customer, session):
        """Test request creation."""
        request = BookRequest(
            customer_id=customer.id,
            title='Wanted Book',
            author='Famous Author',
            min_condition=3
        )
        session.add(request)
        session.flush()
        
        assert request.id is not None
        assert request.status == 'pending'
    
    def test_min_condition_label(self, book_request, session):
        """Test min_condition_label property."""
        book_request.min_condition = 3
        assert book_request.min_condition_label == 'Good'
        
        book_request.min_condition = 5
        assert book_request.min_condition_label == 'Fine'
    
    def test_is_expired(self, book_request, session):
        """Test is_expired property."""
        # Not expired - no expiry set
        book_request.expires_at = None
        assert book_request.is_expired is False
        
        # Not expired - future date
        book_request.expires_at = datetime.utcnow() + timedelta(days=30)
        assert book_request.is_expired is False
        
        # Expired - past date
        book_request.expires_at = datetime.utcnow() - timedelta(days=1)
        assert book_request.is_expired is True


class TestPurchaseOrderModel:
    """Tests for PurchaseOrder model."""
    
    def test_create_po(self, manufacturer, admin_user, session):
        """Test PO creation."""
        po = PurchaseOrder(
            po_number='PO-TEST-001',
            manufacturer_id=manufacturer.id,
            created_by=admin_user.id,
            status='draft'
        )
        session.add(po)
        session.flush()
        
        assert po.id is not None
        assert po.status == 'draft'
    
    def test_po_total(self, purchase_order, sample_book, session):
        """Test PO total calculation."""
        line1 = POLine(
            purchase_order_id=purchase_order.id,
            book_id=sample_book.id,
            quantity=5,
            unit_cost=Decimal('20.00')
        )
        line2 = POLine(
            purchase_order_id=purchase_order.id,
            book_id=sample_book.id,
            quantity=3,
            unit_cost=Decimal('30.00')
        )
        session.add_all([line1, line2])
        session.flush()
        
        # Total = (5 * 20) + (3 * 30) = 100 + 90 = 190
        assert purchase_order.total == Decimal('190.00')
    
    def test_line_count(self, purchase_order, sample_book, session):
        """Test line_count property."""
        assert purchase_order.line_count == 0
        
        line = POLine(
            purchase_order_id=purchase_order.id,
            book_id=sample_book.id,
            quantity=1,
            unit_cost=Decimal('10.00')
        )
        session.add(line)
        session.flush()
        
        assert purchase_order.line_count == 1


class TestWarehouseModel:
    """Tests for Warehouse model."""
    
    def test_create_warehouse(self, session):
        """Test warehouse creation."""
        warehouse = Warehouse(
            name='Test Warehouse',
            location='123 Test Street',
            capacity=5000
        )
        session.add(warehouse)
        session.flush()
        
        assert warehouse.id is not None
        assert warehouse.is_active is True
    
    def test_warehouse_to_dict(self, warehouse, session):
        """Test to_dict method."""
        data = warehouse.to_dict()
        
        assert 'id' in data
        assert data['name'] == warehouse.name
        assert data['location'] == warehouse.location


class TestAddressModel:
    """Tests for Address model."""
    
    def test_create_address(self, customer, session):
        """Test address creation."""
        address = Address(
            customer_id=customer.id,
            address_type='shipping',
            street='456 Ship Lane',
            city='Shiptown',
            state='ST',
            zip_code='54321',
            country='USA'
        )
        session.add(address)
        session.flush()
        
        assert address.id is not None
    
    def test_formatted_address(self, customer_address, session):
        """Test formatted_address property."""
        formatted = customer_address.formatted_address
        
        assert customer_address.street in formatted
        assert customer_address.city in formatted
        assert customer_address.state in formatted
        assert customer_address.zip_code in formatted


class TestManufacturerModel:
    """Tests for Manufacturer model."""
    
    def test_create_manufacturer(self, session):
        """Test manufacturer creation."""
        manufacturer = Manufacturer(
            name='Test Publisher',
            contact_name='John Contact',
            email='contact@test.com',
            phone='555-1234'
        )
        session.add(manufacturer)
        session.flush()
        
        assert manufacturer.id is not None
        assert manufacturer.is_active is True
    
    def test_to_dict(self, manufacturer, session):
        """Test to_dict method."""
        data = manufacturer.to_dict()
        
        assert 'id' in data
        assert data['name'] == manufacturer.name
        assert data['email'] == manufacturer.email
