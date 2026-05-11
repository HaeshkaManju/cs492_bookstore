"""
Book Request Service
====================

Business logic for customer book requests.
Handles request creation, matching, and fulfillment.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from app.models import BookRequest, Book, Inventory, Customer
from app.repositories import BookRequestRepository, CustomerRepository, BookRepository, InventoryRepository
from app.services.base import BaseService, ValidationError, NotFoundError, ConflictError
from app.utils.validators import validate_book_request_data, validate_condition
from app.extensions import db


class BookRequestService(BaseService[BookRequest]):
    """
    Service for book request operations.
    """
    
    def __init__(
        self,
        repository: BookRequestRepository = None,
        customer_repository: CustomerRepository = None,
        book_repository: BookRepository = None,
        inventory_repository: InventoryRepository = None
    ):
        self.repository = repository or BookRequestRepository()
        self.customer_repository = customer_repository or CustomerRepository()
        self.book_repository = book_repository or BookRepository()
        self.inventory_repository = inventory_repository or InventoryRepository()
    
    # =========================================================================
    # Request Creation
    # =========================================================================
    
    def create_request(
        self,
        customer_id: UUID,
        title: str,
        author: str,
        min_condition: int = 3,
        max_price: Optional[Decimal] = None,
        isbn: Optional[str] = None,
        notes: Optional[str] = None,
        expiry_days: int = 365,
        auto_commit: bool = True
    ) -> BookRequest:
        """
        Create a new book request.
        
        Args:
            customer_id: Customer ID
            title: Book title
            author: Author name
            min_condition: Minimum acceptable condition (1-5)
            max_price: Maximum price (optional)
            isbn: ISBN (optional)
            notes: Additional notes
            expiry_days: Days until request expires
            auto_commit: Whether to commit transaction
            
        Returns:
            Created BookRequest instance
        """
        # Validate inputs
        errors = validate_book_request_data({
            'title': title,
            'author': author,
            'min_condition': min_condition,
            'max_price': max_price,
            'isbn': isbn
        })
        self.validate_and_raise(errors)
        
        # Verify customer exists
        customer = self.customer_repository.get_by_id(customer_id)
        if not customer:
            raise NotFoundError("Customer", customer_id)
        
        # Normalize ISBN
        from app.utils.validators import normalize_isbn
        normalized_isbn = normalize_isbn(isbn) if isbn else None
        
        request = BookRequest(
            customer_id=customer_id,
            title=title.strip(),
            author=author.strip(),
            isbn=normalized_isbn,
            min_condition=min_condition,
            max_price=max_price,
            notes=notes.strip() if notes else None,
            expires_at=datetime.utcnow() + timedelta(days=expiry_days)
        )
        
        db.session.add(request)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return request
    
    # =========================================================================
    # Request Queries
    # =========================================================================
    
    def get_by_customer(
        self,
        customer_id: UUID,
        status: Optional[str] = None,
        active_only: bool = False
    ) -> List[BookRequest]:
        """Get requests for a customer."""
        return self.repository.get_by_customer(customer_id, status, active_only)
    
    def get_pending(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get all pending requests."""
        return self.repository.get_pending(page, per_page)
    
    def get_matched(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get matched requests awaiting notification."""
        return self.repository.get_matched(page, per_page)
    
    def search(
        self,
        query: str,
        status: Optional[str] = None,
        customer_id: Optional[UUID] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Search requests."""
        return self.repository.search(query, status, customer_id, page, per_page)
    
    def get_stats(self) -> Dict[str, int]:
        """Get request statistics by status."""
        return self.repository.get_stats()
    
    # =========================================================================
    # Request Matching
    # =========================================================================
    
    def find_matches_for_inventory(
        self,
        book: Book,
        condition: int,
        price: Decimal
    ) -> List[BookRequest]:
        """
        Find pending requests that match new inventory.
        
        Call this when adding new inventory to find customers to notify.
        
        Args:
            book: Book being added
            condition: Condition grade
            price: List price
            
        Returns:
            List of matching BookRequest instances
        """
        return self.repository.find_matches_for_inventory(book, condition, price)
    
    def match_request(
        self,
        request_id: UUID,
        book_id: UUID,
        inventory_id: UUID,
        auto_commit: bool = True
    ) -> BookRequest:
        """
        Match a request with found inventory.
        
        Args:
            request_id: Request ID
            book_id: Matching book ID
            inventory_id: Matching inventory ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated BookRequest instance
        """
        request = self.get_or_404(request_id, "BookRequest")
        
        if not request.is_pending:
            raise ConflictError(
                f"Cannot match request in status: {request.status}",
                {'current_status': request.status}
            )
        
        # Verify book and inventory exist
        book = self.book_repository.get_by_id(book_id)
        if not book:
            raise NotFoundError("Book", book_id)
        
        inventory = self.inventory_repository.get_by_id(inventory_id)
        if not inventory:
            raise NotFoundError("Inventory", inventory_id)
        
        # Verify inventory matches criteria
        if inventory.condition < request.min_condition:
            raise ValidationError([
                f"Inventory condition ({inventory.condition}) below minimum ({request.min_condition})"
            ])
        
        if request.max_price and inventory.list_price > request.max_price:
            raise ValidationError([
                f"Inventory price ({inventory.list_price}) exceeds maximum ({request.max_price})"
            ])
        
        request.match(book_id, inventory_id)
        
        if auto_commit:
            self.commit()
        
        return request
    
    def notify_customer(
        self,
        request_id: UUID,
        auto_commit: bool = True
    ) -> BookRequest:
        """
        Mark that customer has been notified of match.
        
        Args:
            request_id: Request ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated BookRequest instance
        """
        request = self.get_or_404(request_id, "BookRequest")
        
        if not request.is_matched:
            raise ConflictError(
                f"Cannot notify for request in status: {request.status}",
                {'current_status': request.status}
            )
        
        request.notify_customer()
        
        if auto_commit:
            self.commit()
        
        return request
    
    def fulfill_request(
        self,
        request_id: UUID,
        auto_commit: bool = True
    ) -> BookRequest:
        """
        Mark request as fulfilled (customer purchased).
        
        Args:
            request_id: Request ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated BookRequest instance
        """
        request = self.get_or_404(request_id, "BookRequest")
        
        if request.status not in ('matched', 'notified'):
            raise ConflictError(
                f"Cannot fulfill request in status: {request.status}",
                {'current_status': request.status}
            )
        
        request.fulfill()
        
        if auto_commit:
            self.commit()
        
        return request
    
    def unmatch_request(
        self,
        request_id: UUID,
        auto_commit: bool = True
    ) -> BookRequest:
        """
        Remove match from request (customer declined or inventory sold).
        
        Args:
            request_id: Request ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated BookRequest instance (back to pending)
        """
        request = self.get_or_404(request_id, "BookRequest")
        
        if request.status not in ('matched', 'notified'):
            raise ConflictError(
                f"Cannot unmatch request in status: {request.status}",
                {'current_status': request.status}
            )
        
        request.unmatch()
        
        if auto_commit:
            self.commit()
        
        return request
    
    # =========================================================================
    # Request Cancellation/Expiry
    # =========================================================================
    
    def cancel_request(
        self,
        request_id: UUID,
        auto_commit: bool = True
    ) -> BookRequest:
        """
        Cancel a request.
        
        Args:
            request_id: Request ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Cancelled BookRequest instance
        """
        request = self.get_or_404(request_id, "BookRequest")
        
        if request.status in ('fulfilled', 'cancelled'):
            raise ConflictError(
                f"Cannot cancel request in status: {request.status}",
                {'current_status': request.status}
            )
        
        request.cancel()
        
        if auto_commit:
            self.commit()
        
        return request
    
    def expire_overdue_requests(self) -> int:
        """
        Mark all overdue requests as expired.
        
        Call this periodically (e.g., daily cron job).
        
        Returns:
            Number of requests expired
        """
        return self.repository.expire_overdue()
    
    # =========================================================================
    # Request Updates
    # =========================================================================
    
    def update_request(
        self,
        request_id: UUID,
        title: Optional[str] = None,
        author: Optional[str] = None,
        min_condition: Optional[int] = None,
        max_price: Optional[Decimal] = None,
        notes: Optional[str] = None,
        auto_commit: bool = True
    ) -> BookRequest:
        """
        Update a pending request.
        
        Args:
            request_id: Request ID
            title: New title
            author: New author
            min_condition: New minimum condition
            max_price: New maximum price
            notes: New notes
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated BookRequest instance
        """
        request = self.get_or_404(request_id, "BookRequest")
        
        if not request.is_pending:
            raise ConflictError(
                "Can only update pending requests",
                {'current_status': request.status}
            )
        
        errors = []
        
        if title is not None:
            if not title.strip():
                errors.append("Title cannot be empty")
            else:
                request.title = title.strip()
        
        if author is not None:
            if not author.strip():
                errors.append("Author cannot be empty")
            else:
                request.author = author.strip()
        
        if min_condition is not None:
            is_valid, error = validate_condition(min_condition)
            if not is_valid:
                errors.append(f"Minimum condition: {error}")
            else:
                request.min_condition = min_condition
        
        if max_price is not None:
            request.max_price = max_price if max_price > 0 else None
        
        self.validate_and_raise(errors)
        
        if notes is not None:
            request.notes = notes.strip() if notes else None
        
        if auto_commit:
            self.commit()
        
        return request
