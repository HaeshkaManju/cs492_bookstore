"""
Book Schemas
============

DTOs for book catalog API operations.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.schemas.base import BaseSchema


@dataclass
class BookSchema(BaseSchema):
    """Schema for book responses."""
    
    id: UUID
    isbn: Optional[str]
    title: str
    author: str
    publisher: Optional[str]
    year_published: Optional[int]
    description: Optional[str]
    category: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # Optional computed fields
    total_quantity: Optional[int] = None
    lowest_price: Optional[float] = None
    in_stock: Optional[bool] = None
    
    @classmethod
    def from_model(cls, model, include_inventory_stats: bool = False) -> 'BookSchema':
        total_qty = None
        lowest_price = None
        in_stock = None
        
        if include_inventory_stats:
            total_qty = model.get_total_quantity()
            lowest_price = model.get_lowest_price()
            in_stock = total_qty > 0 if total_qty is not None else None
        
        return cls(
            id=model.id,
            isbn=model.isbn,
            title=model.title,
            author=model.author,
            publisher=model.publisher,
            year_published=model.year_published,
            description=model.description,
            category=model.category,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            total_quantity=total_qty,
            lowest_price=lowest_price,
            in_stock=in_stock
        )


@dataclass
class BookCreateSchema(BaseSchema):
    """Schema for book creation requests."""
    
    title: str
    author: str
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    year_published: Optional[int] = None
    description: Optional[str] = None
    category: Optional[str] = None
    
    def validate(self) -> list:
        """Validate book data."""
        from app.utils.validators import validate_book_data
        return validate_book_data({
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'year_published': self.year_published
        })


@dataclass
class BookUpdateSchema(BaseSchema):
    """Schema for book update requests."""
    
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    year_published: Optional[int] = None
    description: Optional[str] = None
    category: Optional[str] = None
    
    def validate(self) -> list:
        """Validate book update data."""
        errors = []
        
        if self.title is not None and not self.title.strip():
            errors.append("Title cannot be empty")
        
        if self.author is not None and not self.author.strip():
            errors.append("Author cannot be empty")
        
        if self.isbn:
            from app.utils.validators import validate_isbn
            is_valid, error = validate_isbn(self.isbn)
            if not is_valid:
                errors.append(f"ISBN: {error}")
        
        if self.year_published is not None:
            if self.year_published < 1000 or self.year_published > 2100:
                errors.append("Year must be between 1000 and 2100")
        
        return errors


@dataclass
class BookSearchSchema(BaseSchema):
    """Schema for book search parameters."""
    
    query: str = ''
    category: Optional[str] = None
    in_stock_only: bool = False
    page: int = 1
    per_page: int = 20
