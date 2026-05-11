"""
Book Request Repository
=======================

Data access for BookRequest model.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, and_, or_

from app.models import BookRequest, Customer, Book, Inventory
from app.repositories.base import BaseRepository
from app.extensions import db


class BookRequestRepository(BaseRepository[BookRequest]):
    """
    Repository for BookRequest data access.
    """
    
    model_class = BookRequest
    
    def get_by_customer(
        self,
        customer_id: UUID,
        status: Optional[str] = None,
        active_only: bool = False
    ) -> List[BookRequest]:
        """
        Get requests for a customer.
        
        Args:
            customer_id: Customer ID
            status: Optional status filter
            active_only: Only return active (pending/matched/notified) requests
            
        Returns:
            List of BookRequest instances
        """
        query = BookRequest.query.filter_by(customer_id=customer_id)
        
        if status:
            query = query.filter_by(status=status)
        elif active_only:
            query = query.filter(
                BookRequest.status.in_(['pending', 'matched', 'notified'])
            )
        
        return query.order_by(BookRequest.created_at.desc()).all()
    
    def get_pending(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get all pending requests.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        query = BookRequest.query.filter_by(
            status='pending'
        ).filter(
            BookRequest.expires_at > datetime.utcnow()
        ).order_by(BookRequest.created_at.asc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    
    def get_matched(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get all matched requests awaiting notification.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        query = BookRequest.query.filter_by(
            status='matched'
        ).order_by(BookRequest.updated_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    
    def get_expired(self) -> List[BookRequest]:
        """
        Get requests past expiry date that need to be marked expired.
        
        Returns:
            List of expired BookRequest instances
        """
        return BookRequest.query.filter(
            BookRequest.status.in_(['pending', 'matched', 'notified']),
            BookRequest.expires_at < datetime.utcnow()
        ).all()
    
    def find_matches_for_inventory(
        self,
        book: Book,
        condition: int,
        price: Decimal
    ) -> List[BookRequest]:
        """
        Find pending requests that match new inventory.
        
        Args:
            book: Book being added
            condition: Condition grade
            price: List price
            
        Returns:
            List of matching BookRequest instances
        """
        # Build title/author search pattern
        title_pattern = f"%{book.title.lower()}%"
        author_pattern = f"%{book.author.lower()}%"
        
        query = BookRequest.query.filter(
            BookRequest.status == 'pending',
            BookRequest.min_condition <= condition,
            BookRequest.expires_at > datetime.utcnow()
        )
        
        # Price filter (max_price is optional)
        query = query.filter(
            or_(
                BookRequest.max_price.is_(None),
                BookRequest.max_price >= price
            )
        )
        
        # Title/author matching
        query = query.filter(
            or_(
                func.lower(BookRequest.title).contains(book.title.lower()),
                func.lower(book.title).contains(func.lower(BookRequest.title))
            )
        )
        
        # ISBN exact match (if provided)
        if book.isbn:
            normalized_isbn = book.isbn.replace('-', '').replace(' ', '')
            query = query.filter(
                or_(
                    BookRequest.isbn.is_(None),
                    func.replace(func.replace(BookRequest.isbn, '-', ''), ' ', '') == normalized_isbn
                )
            )
        
        return query.all()
    
    def search(
        self,
        query_str: str,
        status: Optional[str] = None,
        customer_id: Optional[UUID] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search requests by title/author.
        
        Args:
            query_str: Search string
            status: Optional status filter
            customer_id: Optional customer filter
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        search = f"%{query_str}%"
        
        query = BookRequest.query.filter(
            or_(
                BookRequest.title.ilike(search),
                BookRequest.author.ilike(search),
                BookRequest.isbn.ilike(search)
            )
        )
        
        if status:
            query = query.filter_by(status=status)
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        query = query.order_by(BookRequest.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get request statistics by status.
        
        Returns:
            Dict mapping status to count
        """
        results = db.session.query(
            BookRequest.status,
            func.count(BookRequest.id)
        ).group_by(BookRequest.status).all()
        
        return {status: count for status, count in results}
    
    def expire_overdue(self) -> int:
        """
        Mark overdue requests as expired.
        
        Returns:
            Number of requests expired
        """
        count = BookRequest.query.filter(
            BookRequest.status.in_(['pending', 'matched', 'notified']),
            BookRequest.expires_at < datetime.utcnow()
        ).update(
            {'status': 'expired'},
            synchronize_session='fetch'
        )
        
        db.session.commit()
        return count
