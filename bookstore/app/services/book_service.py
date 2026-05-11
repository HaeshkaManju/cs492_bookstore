"""
Book Service
============

Business logic for book catalog management.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from app.models import Book
from app.repositories import BookRepository
from app.services.base import BaseService, ValidationError, ConflictError
from app.utils.validators import validate_book_data, validate_isbn, normalize_isbn
from app.extensions import db


class BookService(BaseService[Book]):
    """
    Service for book catalog operations.
    """
    
    def __init__(self, repository: BookRepository = None):
        self.repository = repository or BookRepository()
    
    # =========================================================================
    # Book Creation
    # =========================================================================
    
    def create_book(
        self,
        title: str,
        author: str,
        isbn: Optional[str] = None,
        publisher: Optional[str] = None,
        year_published: Optional[int] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        auto_commit: bool = True
    ) -> Book:
        """
        Create a new book catalog entry.
        
        Args:
            title: Book title
            author: Author name
            isbn: ISBN (optional)
            publisher: Publisher name
            year_published: Publication year
            description: Book description
            category: Book category
            auto_commit: Whether to commit transaction
            
        Returns:
            Created Book instance
        """
        # Validate inputs
        errors = validate_book_data({
            'title': title,
            'author': author,
            'isbn': isbn,
            'year_published': year_published
        })
        self.validate_and_raise(errors)
        
        # Check ISBN uniqueness if provided
        normalized_isbn = normalize_isbn(isbn) if isbn else None
        if normalized_isbn:
            existing = self.repository.get_by_isbn(normalized_isbn)
            if existing:
                raise ConflictError(
                    "A book with this ISBN already exists",
                    {'isbn': isbn, 'existing_book_id': str(existing.id)}
                )
        
        book = Book(
            isbn=normalized_isbn,
            title=title.strip(),
            author=author.strip(),
            publisher=publisher.strip() if publisher else None,
            year_published=year_published,
            description=description.strip() if description else None,
            category=category.strip() if category else None
        )
        
        db.session.add(book)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return book
    
    # =========================================================================
    # Book Queries
    # =========================================================================
    
    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        """Find book by ISBN."""
        return self.repository.get_by_isbn(isbn)
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        in_stock_only: bool = False,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search books by title, author, or ISBN.
        
        Args:
            query: Search string
            category: Optional category filter
            in_stock_only: Only return books with inventory
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        return self.repository.search(
            query_str=query,
            category=category,
            in_stock_only=in_stock_only,
            page=page,
            per_page=per_page
        )
    
    def get_by_author(self, author: str) -> List[Book]:
        """Get all books by an author."""
        return self.repository.get_by_author(author)
    
    def get_by_category(self, category: str) -> List[Book]:
        """Get all books in a category."""
        return self.repository.get_by_category(category)
    
    def get_categories(self) -> List[str]:
        """Get list of all unique categories."""
        return self.repository.get_categories()
    
    def get_in_stock(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get books with inventory in stock."""
        return self.repository.get_in_stock(page, per_page)
    
    def get_recently_added(self, limit: int = 10) -> List[Book]:
        """Get most recently added books."""
        return self.repository.get_recently_added(limit)
    
    def get_with_inventory(self, book_id: UUID) -> Optional[Book]:
        """Get book with inventory data."""
        return self.repository.get_with_inventory(book_id)
    
    # =========================================================================
    # Book Updates
    # =========================================================================
    
    def update_book(
        self,
        book_id: UUID,
        title: Optional[str] = None,
        author: Optional[str] = None,
        isbn: Optional[str] = None,
        publisher: Optional[str] = None,
        year_published: Optional[int] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        auto_commit: bool = True
    ) -> Book:
        """
        Update a book entry.
        
        Args:
            book_id: Book ID
            title: New title
            author: New author
            isbn: New ISBN
            publisher: New publisher
            year_published: New publication year
            description: New description
            category: New category
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated Book instance
        """
        book = self.get_or_404(book_id, "Book")
        
        errors = []
        
        if title is not None:
            if not title.strip():
                errors.append("Title cannot be empty")
            else:
                book.title = title.strip()
        
        if author is not None:
            if not author.strip():
                errors.append("Author cannot be empty")
            else:
                book.author = author.strip()
        
        if isbn is not None:
            if isbn:
                is_valid, error = validate_isbn(isbn)
                if not is_valid:
                    errors.append(f"ISBN: {error}")
                else:
                    normalized = normalize_isbn(isbn)
                    # Check uniqueness excluding current book
                    existing = self.repository.get_by_isbn(normalized)
                    if existing and existing.id != book_id:
                        errors.append("ISBN is already used by another book")
                    else:
                        book.isbn = normalized
            else:
                book.isbn = None
        
        if year_published is not None:
            if year_published and (year_published < 1000 or year_published > 2100):
                errors.append("Year must be between 1000 and 2100")
            else:
                book.year_published = year_published
        
        self.validate_and_raise(errors)
        
        if publisher is not None:
            book.publisher = publisher.strip() if publisher else None
        
        if description is not None:
            book.description = description.strip() if description else None
        
        if category is not None:
            book.category = category.strip() if category else None
        
        if auto_commit:
            self.commit()
        
        return book
    
    def deactivate_book(self, book_id: UUID, auto_commit: bool = True) -> Book:
        """
        Deactivate a book (soft delete).
        
        Args:
            book_id: Book ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Deactivated Book instance
        """
        book = self.get_or_404(book_id, "Book")
        book.is_active = False
        
        if auto_commit:
            self.commit()
        
        return book
    
    def reactivate_book(self, book_id: UUID, auto_commit: bool = True) -> Book:
        """
        Reactivate a deactivated book.
        
        Args:
            book_id: Book ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Reactivated Book instance
        """
        book = self.get_or_404(book_id, "Book")
        book.is_active = True
        
        if auto_commit:
            self.commit()
        
        return book
