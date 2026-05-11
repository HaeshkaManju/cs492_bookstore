"""
Service Layer
=============

Business logic layer implementing the Service Pattern.

Design Pattern: Service Layer Pattern + Dependency Injection
- Services encapsulate business logic
- Services use repositories for data access
- Services are stateless and testable
- Dependency injection allows easy mocking for tests

Architecture:
- Each service handles one domain concern
- Services call repositories, never access db directly
- Services can call other services for cross-domain operations
- Services return DTOs for API responses

Usage:
    from app.services import BookService, InventoryService
    
    # Create service instance
    book_service = BookService()
    
    # Use service methods
    book = book_service.create_book(title='Clean Code', author='Robert Martin')
    inventory = InventoryService().add_inventory(book.id, warehouse_id, condition=4)

Integration Points:
- API routes call services
- Services call repositories
- Services emit events for cross-module communication (future)
"""

from app.services.user_service import UserService
from app.services.customer_service import CustomerService
from app.services.book_service import BookService
from app.services.inventory_service import InventoryService
from app.services.invoice_service import InvoiceService
from app.services.book_request_service import BookRequestService
from app.services.purchase_order_service import PurchaseOrderService

__all__ = [
    'UserService',
    'CustomerService',
    'BookService',
    'InventoryService',
    'InvoiceService',
    'BookRequestService',
    'PurchaseOrderService',
]
