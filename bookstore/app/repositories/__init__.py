"""
Repository Layer
================

Implements the Repository Pattern for data access abstraction.

Design Pattern: Repository Pattern
- Separates domain logic from data access
- Provides clean interfaces for CRUD operations
- Enables easy testing with mock repositories
- Allows swapping data sources without changing business logic

Architecture:
- BaseRepository: Common CRUD operations
- Domain-specific repositories: Custom queries and business operations

Usage:
    from app.repositories import BookRepository, InventoryRepository
    
    # Get repository instance
    book_repo = BookRepository()
    
    # Find books by author
    books = book_repo.find_by_author('Robert Martin')
    
    # Create new book
    book = book_repo.create(title='Clean Code', author='Robert Martin')

Integration Points:
- Services use repositories for data access
- Repositories use SQLAlchemy models for persistence
- API layer injects repositories into services
"""

from app.repositories.base import BaseRepository
from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.book_repository import BookRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.book_request_repository import BookRequestRepository
from app.repositories.purchase_order_repository import PurchaseOrderRepository

__all__ = [
    'BaseRepository',
    'UserRepository',
    'CustomerRepository',
    'BookRepository',
    'InventoryRepository',
    'InvoiceRepository',
    'BookRequestRepository',
    'PurchaseOrderRepository',
]
