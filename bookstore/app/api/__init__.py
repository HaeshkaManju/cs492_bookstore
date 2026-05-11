"""
API Integration Layer
=====================

Provides clean API interfaces for module integration.

Design Pattern: Facade Pattern
- Simplifies complex subsystem interactions
- Provides unified interface for external consumers
- Enables loose coupling between modules

This module exposes:
- Service factory functions
- API response helpers
- Module registration for Flask blueprints

Usage:
    from app.api import get_book_service, get_inventory_service
    
    book_service = get_book_service()
    books = book_service.search("Python")

Integration Points:
- RBAC team can wrap services with permission checks
- API routes use these factories for service instances
- Testing can inject mock services
"""

from typing import Dict, Any, Optional
from functools import lru_cache

# Service factories - cached for performance
from app.services import (
    UserService,
    CustomerService,
    BookService,
    InventoryService,
    InvoiceService,
    BookRequestService,
    PurchaseOrderService
)


# =============================================================================
# Service Factory Functions
# =============================================================================

@lru_cache(maxsize=1)
def get_user_service() -> UserService:
    """Get singleton UserService instance."""
    return UserService()


@lru_cache(maxsize=1)
def get_customer_service() -> CustomerService:
    """Get singleton CustomerService instance."""
    return CustomerService()


@lru_cache(maxsize=1)
def get_book_service() -> BookService:
    """Get singleton BookService instance."""
    return BookService()


@lru_cache(maxsize=1)
def get_inventory_service() -> InventoryService:
    """Get singleton InventoryService instance."""
    return InventoryService()


@lru_cache(maxsize=1)
def get_invoice_service() -> InvoiceService:
    """Get singleton InvoiceService instance."""
    return InvoiceService()


@lru_cache(maxsize=1)
def get_book_request_service() -> BookRequestService:
    """Get singleton BookRequestService instance."""
    return BookRequestService()


@lru_cache(maxsize=1)
def get_purchase_order_service() -> PurchaseOrderService:
    """Get singleton PurchaseOrderService instance."""
    return PurchaseOrderService()


def clear_service_cache():
    """Clear cached service instances (for testing)."""
    get_user_service.cache_clear()
    get_customer_service.cache_clear()
    get_book_service.cache_clear()
    get_inventory_service.cache_clear()
    get_invoice_service.cache_clear()
    get_book_request_service.cache_clear()
    get_purchase_order_service.cache_clear()


# =============================================================================
# API Response Helpers
# =============================================================================

def api_success(
    data: Any = None,
    message: str = None,
    status: int = 200
) -> tuple:
    """
    Create successful API response.
    
    Args:
        data: Response data
        message: Optional success message
        status: HTTP status code
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {'success': True}
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    return response, status


def api_error(
    message: str,
    code: str = 'ERROR',
    details: Dict = None,
    status: int = 400
) -> tuple:
    """
    Create error API response.
    
    Args:
        message: Error message
        code: Error code
        details: Additional error details
        status: HTTP status code
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        'success': False,
        'error': {
            'code': code,
            'message': message
        }
    }
    
    if details:
        response['error']['details'] = details
    
    return response, status


def api_validation_error(errors: list) -> tuple:
    """
    Create validation error response.
    
    Args:
        errors: List of validation error messages
        
    Returns:
        Tuple of (response_dict, 400)
    """
    return api_error(
        message="Validation failed",
        code="VALIDATION_ERROR",
        details={'errors': errors},
        status=400
    )


def api_not_found(resource: str, id: Any = None) -> tuple:
    """
    Create not found error response.
    
    Args:
        resource: Resource type name
        id: Optional resource ID
        
    Returns:
        Tuple of (response_dict, 404)
    """
    message = f"{resource} not found"
    if id:
        message = f"{resource} not found: {id}"
    
    return api_error(
        message=message,
        code="NOT_FOUND",
        status=404
    )


def api_paginated(
    items: list,
    total: int,
    page: int,
    per_page: int,
    pages: int
) -> tuple:
    """
    Create paginated API response.
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        per_page: Items per page
        pages: Total number of pages
        
    Returns:
        Tuple of (response_dict, 200)
    """
    return api_success({
        'items': items,
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pages,
            'has_next': page < pages,
            'has_prev': page > 1
        }
    })


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Service factories
    'get_user_service',
    'get_customer_service',
    'get_book_service',
    'get_inventory_service',
    'get_invoice_service',
    'get_book_request_service',
    'get_purchase_order_service',
    'clear_service_cache',
    
    # Response helpers
    'api_success',
    'api_error',
    'api_validation_error',
    'api_not_found',
    'api_paginated',
]
