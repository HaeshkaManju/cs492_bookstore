"""
Service Layer Tests
===================

Tests for business logic services.
"""

import pytest
from decimal import Decimal
from uuid import uuid4

from app.services.base import ValidationError, NotFoundError, ConflictError


class TestUserService:
    """Tests for UserService."""
    
    def test_create_user(self, user_service, session):
        """Test user creation."""
        user = user_service.create_user(
            email='newuser@test.com',
            password='SecurePass123!',
            first_name='New',
            last_name='User',
            role='customer',
            auto_commit=False
        )
        
        assert user.id is not None
        assert user.email == 'newuser@test.com'
        assert user.check_password('SecurePass123!')
    
    def test_create_user_duplicate_email(self, user_service, admin_user, session):
        """Test duplicate email prevention."""
        with pytest.raises(ConflictError):
            user_service.create_user(
                email=admin_user.email,
                password='SecurePass123!',
                first_name='Dup',
                last_name='User',
                role='customer',
                auto_commit=False
            )
    
    def test_create_user_weak_password(self, user_service, session):
        """Test weak password rejection."""
        with pytest.raises(ValidationError) as exc_info:
            user_service.create_user(
                email='weak@test.com',
                password='weak',
                first_name='Weak',
                last_name='User',
                role='customer',
                auto_commit=False
            )
        
        assert 'Password' in str(exc_info.value.errors)
    
    def test_authenticate(self, user_service, admin_user, session):
        """Test user authentication."""
        user = user_service.authenticate(
            email=admin_user.email,
            password='AdminPass123!'
        )
        
        assert user is not None
        assert user.id == admin_user.id
    
    def test_authenticate_wrong_password(self, user_service, admin_user, session):
        """Test authentication with wrong password."""
        user = user_service.authenticate(
            email=admin_user.email,
            password='WrongPassword'
        )
        
        assert user is None
    
    def test_deactivate_user(self, user_service, customer_user, session):
        """Test user deactivation."""
        user_service.deactivate_user(customer_user.id, auto_commit=False)
        
        assert not customer_user.is_active
        
        # Deactivated user cannot authenticate
        result = user_service.authenticate(
            email=customer_user.email,
            password='CustomerPass123!'
        )
        assert result is None


class TestBookService:
    """Tests for BookService."""
    
    def test_create_book(self, book_service, session):
        """Test book creation."""
        book = book_service.create_book(
            title='New Book',
            author='New Author',
            isbn='978-0-321-12521-7',
            category='Testing',
            auto_commit=False
        )
        
        assert book.id is not None
        assert book.title == 'New Book'
    
    def test_create_book_duplicate_isbn(self, book_service, sample_book, session):
        """Test duplicate ISBN prevention."""
        with pytest.raises(ConflictError):
            book_service.create_book(
                title='Another Book',
                author='Another Author',
                isbn=sample_book.isbn,
                auto_commit=False
            )
    
    def test_search_books(self, book_service, multiple_books, session):
        """Test book search."""
        results = book_service.search(query='Code')
        
        assert results['total'] >= 1
        assert any('Code' in b.title for b in results['items'])
    
    def test_get_by_author(self, book_service, multiple_books, session):
        """Test get books by author."""
        books = book_service.get_by_author('Martin')
        
        assert len(books) >= 1
        assert all('Martin' in b.author for b in books)


class TestInventoryService:
    """Tests for InventoryService."""
    
    def test_add_inventory(self, inventory_service, sample_book, warehouse, session):
        """Test adding inventory."""
        inventory = inventory_service.add_inventory(
            book_id=sample_book.id,
            warehouse_id=warehouse.id,
            condition=3,
            quantity=10,
            acquisition_cost=Decimal('15.00'),
            list_price=Decimal('29.99'),
            auto_commit=False
        )
        
        assert inventory.id is not None
        assert inventory.quantity == 10
    
    def test_add_inventory_existing(self, inventory_service, inventory, session):
        """Test adding to existing inventory."""
        original_qty = inventory.quantity
        
        # Add more of same book/warehouse/condition
        result = inventory_service.add_inventory(
            book_id=inventory.book_id,
            warehouse_id=inventory.warehouse_id,
            condition=inventory.condition,
            quantity=5,
            acquisition_cost=Decimal('25.00'),
            list_price=Decimal('49.99'),
            auto_commit=False
        )
        
        assert result.quantity == original_qty + 5
    
    def test_reserve_inventory(self, inventory_service, inventory, session):
        """Test reserving inventory."""
        original_qty = inventory.quantity
        
        inventory_service.reserve_inventory(
            inventory_id=inventory.id,
            quantity=2,
            auto_commit=False
        )
        
        assert inventory.quantity == original_qty - 2
    
    def test_reserve_insufficient(self, inventory_service, inventory, session):
        """Test reserving more than available."""
        with pytest.raises(ValidationError):
            inventory_service.reserve_inventory(
                inventory_id=inventory.id,
                quantity=100,
                auto_commit=False
            )
    
    def test_get_low_stock(self, inventory_service, inventory, session):
        """Test low stock detection."""
        inventory.quantity = 1
        inventory.reorder_level = 2
        session.flush()
        
        low_stock = inventory_service.get_low_stock()
        
        assert any(i.id == inventory.id for i in low_stock)


class TestInvoiceService:
    """Tests for InvoiceService."""
    
    def test_create_invoice(self, invoice_service, customer, admin_user, session):
        """Test invoice creation."""
        invoice = invoice_service.create_invoice(
            customer_id=customer.id,
            created_by=admin_user.id,
            auto_commit=False
        )
        
        assert invoice.id is not None
        assert invoice.status == 'draft'
        assert invoice.invoice_number.startswith('INV-')
    
    def test_add_inventory_line(
        self, invoice_service, invoice, inventory, session
    ):
        """Test adding inventory line to invoice."""
        line = invoice_service.add_inventory_line(
            invoice_id=invoice.id,
            inventory_id=inventory.id,
            quantity=1,
            auto_commit=False
        )
        
        assert line.id is not None
        assert line.unit_price == inventory.list_price
        assert invoice.subtotal > 0
    
    def test_send_invoice(self, invoice_service, invoice, inventory, session):
        """Test sending invoice."""
        # Add line first
        invoice_service.add_inventory_line(
            invoice_id=invoice.id,
            inventory_id=inventory.id,
            quantity=1,
            auto_commit=False
        )
        
        invoice_service.send_invoice(invoice.id, auto_commit=False)
        
        assert invoice.status == 'sent'
        assert invoice.sent_at is not None
    
    def test_send_empty_invoice(self, invoice_service, invoice, session):
        """Test cannot send empty invoice."""
        with pytest.raises(ValidationError):
            invoice_service.send_invoice(invoice.id, auto_commit=False)


class TestBookRequestService:
    """Tests for BookRequestService."""
    
    def test_create_request(self, book_request_service, customer, session):
        """Test request creation."""
        request = book_request_service.create_request(
            customer_id=customer.id,
            title='Wanted Book',
            author='Famous Author',
            min_condition=3,
            auto_commit=False
        )
        
        assert request.id is not None
        assert request.status == 'pending'
    
    def test_match_request(
        self, book_request_service, book_request, sample_book, inventory, session
    ):
        """Test matching request with inventory."""
        book_request_service.match_request(
            request_id=book_request.id,
            book_id=sample_book.id,
            inventory_id=inventory.id,
            auto_commit=False
        )
        
        assert book_request.status == 'matched'
        assert book_request.matched_book_id == sample_book.id
    
    def test_fulfill_request(
        self, book_request_service, book_request, sample_book, inventory, session
    ):
        """Test fulfilling request."""
        # Match first
        book_request_service.match_request(
            request_id=book_request.id,
            book_id=sample_book.id,
            inventory_id=inventory.id,
            auto_commit=False
        )
        
        book_request_service.fulfill_request(book_request.id, auto_commit=False)
        
        assert book_request.status == 'fulfilled'
