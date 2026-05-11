"""
Domain Models
=============

This package contains all SQLAlchemy domain models for the bookstore system.
Models are organized by domain concern following Domain-Driven Design principles.

Architecture:
- Each model file represents a bounded context
- Models use composition over inheritance where possible
- Base classes provide common functionality (timestamps, soft delete)

Usage:
    from app.models import User, Customer, Book, Inventory
    
    # Create a new user
    user = User(email='test@example.com', first_name='John', last_name='Doe')
    user.set_password('secure_password')
    
    # Query inventory
    low_stock = Inventory.get_low_stock_items()

Design Patterns Used:
- Repository Pattern: See app/repositories/ for data access
- Active Record: Models have data access methods
- Template Method: Base classes define common behavior
"""

# Base classes
from app.models.base import (
    BaseModel,
    AuditableModel,
    TimestampMixin,
    SoftDeleteMixin,
    UUIDMixin
)

# User and Customer domain
from app.models.user import User
from app.models.customer import Customer, Address

# Book catalog domain
from app.models.book import Book

# Inventory domain
from app.models.inventory import (
    Inventory,
    Warehouse,
    CONDITION_FINE,
    CONDITION_VERY_GOOD,
    CONDITION_GOOD,
    CONDITION_FAIR,
    CONDITION_POOR,
    CONDITION_LABELS
)

# Invoice domain
from app.models.invoice import (
    Invoice,
    InvoiceLine,
    STATUS_DRAFT as INVOICE_STATUS_DRAFT,
    STATUS_SENT as INVOICE_STATUS_SENT,
    STATUS_PAID as INVOICE_STATUS_PAID,
    STATUS_CANCELLED as INVOICE_STATUS_CANCELLED
)

# Book request domain
from app.models.book_request import (
    BookRequest,
    STATUS_PENDING as REQUEST_STATUS_PENDING,
    STATUS_MATCHED as REQUEST_STATUS_MATCHED,
    STATUS_NOTIFIED as REQUEST_STATUS_NOTIFIED,
    STATUS_FULFILLED as REQUEST_STATUS_FULFILLED,
    STATUS_EXPIRED as REQUEST_STATUS_EXPIRED,
    STATUS_CANCELLED as REQUEST_STATUS_CANCELLED
)

# Purchase order domain
from app.models.purchase_order import (
    Manufacturer,
    PurchaseOrder,
    POLine,
    STATUS_DRAFT as PO_STATUS_DRAFT,
    STATUS_SUBMITTED as PO_STATUS_SUBMITTED,
    STATUS_CONFIRMED as PO_STATUS_CONFIRMED,
    STATUS_SHIPPED as PO_STATUS_SHIPPED,
    STATUS_RECEIVED as PO_STATUS_RECEIVED,
    STATUS_CANCELLED as PO_STATUS_CANCELLED
)

# All models for convenient import
__all__ = [
    # Base
    'BaseModel',
    'AuditableModel',
    'TimestampMixin',
    'SoftDeleteMixin',
    'UUIDMixin',
    
    # User domain
    'User',
    'Customer',
    'Address',
    
    # Book domain
    'Book',
    
    # Inventory domain
    'Inventory',
    'Warehouse',
    'CONDITION_FINE',
    'CONDITION_VERY_GOOD',
    'CONDITION_GOOD',
    'CONDITION_FAIR',
    'CONDITION_POOR',
    'CONDITION_LABELS',
    
    # Invoice domain
    'Invoice',
    'InvoiceLine',
    'INVOICE_STATUS_DRAFT',
    'INVOICE_STATUS_SENT',
    'INVOICE_STATUS_PAID',
    'INVOICE_STATUS_CANCELLED',
    
    # Book request domain
    'BookRequest',
    'REQUEST_STATUS_PENDING',
    'REQUEST_STATUS_MATCHED',
    'REQUEST_STATUS_NOTIFIED',
    'REQUEST_STATUS_FULFILLED',
    'REQUEST_STATUS_EXPIRED',
    'REQUEST_STATUS_CANCELLED',
    
    # Purchase order domain
    'Manufacturer',
    'PurchaseOrder',
    'POLine',
    'PO_STATUS_DRAFT',
    'PO_STATUS_SUBMITTED',
    'PO_STATUS_CONFIRMED',
    'PO_STATUS_SHIPPED',
    'PO_STATUS_RECEIVED',
    'PO_STATUS_CANCELLED',
]
