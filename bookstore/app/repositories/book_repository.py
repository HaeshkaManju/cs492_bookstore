"""
Book Repository
===============

Data access for Book model.
Provides book catalog queries including search and filtering.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import func, or_

from app.models import Book, Inventory
from app.repositories.base import BaseRepository
from app.extensions import db


class BookRepository(BaseRepository[Book]):
    """
    Repository for Book catalog data access.
    """
    
    model_class = Book
    
    def _active_query(self):
        """Override to filter active books by default."""
        return Book.query.filter_by(is_active=True)
    
    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        """
        Find book by ISBN.
        
        Args:
            isbn: ISBN-10 or ISBN-13 (with or without hyphens)
            
        Returns:
            Book instance or None
        """
        # Normalize ISBN for comparison
        cleaned = isbn.replace('-', '').replace(' ', '').upper()
        
        return Book.query.filter(
            func.replace(func.replace(func.upper(Book.isbn), '-', ''), ' ', '') == cleaned
        ).first()
    
    def search(
        self,
        query_str: str,
        category: Optional[str] = None,
        in_stock_only: bool = False,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search books by title, author, or ISBN.
        
        Args:
            query_str: Search string
            category: Optional category filter
            in_stock_only: Only return books with inventory
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        search = f"%{query_str}%"
        
        query = self._active_query().filter(
            or_(
                Book.title.ilike(search),
                Book.author.ilike(search),
                Book.isbn.ilike(search)
            )
        )
        
        if category:
            query = query.filter(Book.category == category)
        
        if in_stock_only:
            query = query.join(Inventory).filter(Inventory.quantity > 0).distinct()
        
        query = query.order_by(Book.title)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    
    def get_by_author(
        self,
        author: str,
        active_only: bool = True
    ) -> List[Book]:
        """
        Get all books by an author.
        
        Args:
            author: Author name (partial match)
            active_only: Only return active books
            
        Returns:
            List of Book instances
        """
        query = Book.query.filter(Book.author.ilike(f"%{author}%"))
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.order_by(Book.year_published.desc(), Book.title).all()
    
    def get_by_category(
        self,
        category: str,
        active_only: bool = True
    ) -> List[Book]:
        """
        Get all books in a category.
        
        Args:
            category: Category name
            active_only: Only return active books
            
        Returns:
            List of Book instances
        """
        query = Book.query.filter_by(category=category)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.order_by(Book.title).all()
    
    def get_categories(self) -> List[str]:
        """
        Get list of all unique categories.
        
        Returns:
            List of category names
        """
        results = db.session.query(Book.category).filter(
            Book.category.isnot(None),
            Book.is_active == True
        ).distinct().order_by(Book.category).all()
        
        return [r[0] for r in results]
    
    def get_in_stock(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get books that have inventory in stock.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        query = self._active_query().join(Inventory).filter(
            Inventory.quantity > 0
        ).distinct().order_by(Book.title)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    
    def get_recently_added(self, limit: int = 10) -> List[Book]:
        """
        Get most recently added books.
        
        Args:
            limit: Number of books to return
            
        Returns:
            List of Book instances
        """
        return self._active_query().order_by(
            Book.created_at.desc()
        ).limit(limit).all()
    
    def get_with_inventory(self, book_id: UUID) -> Optional[Book]:
        """
        Get book with inventory data eagerly loaded.
        
        Args:
            book_id: Book ID
            
        Returns:
            Book instance with inventory
        """
        return Book.query.options(
            db.joinedload(Book.inventory_items)
        ).get(book_id)
