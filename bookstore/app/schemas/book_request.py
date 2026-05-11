"""
Book Request Schemas
====================

DTOs for book request API operations.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.schemas.base import BaseSchema
from app.models.inventory import CONDITION_LABELS


@dataclass
class BookRequestSchema(BaseSchema):
    """Schema for book request responses."""
    
    id: UUID
    customer_id: UUID
    isbn: Optional[str]
    title: str
    author: str
    min_condition: int
    min_condition_label: str
    max_price: Optional[float]
    status: str
    matched_book_id: Optional[UUID]
    matched_inventory_id: Optional[UUID]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    # Optional joined data
    customer_name: Optional[str] = None
    matched_book_title: Optional[str] = None
    is_overdue: Optional[bool] = None
    
    @classmethod
    def from_model(cls, model, include_related: bool = True) -> 'BookRequestSchema':
        customer_name = None
        matched_book_title = None
        
        if include_related:
            if model.customer:
                customer_name = model.customer.display_name
            if model.matched_book:
                matched_book_title = model.matched_book.title
        
        return cls(
            id=model.id,
            customer_id=model.customer_id,
            isbn=model.isbn,
            title=model.title,
            author=model.author,
            min_condition=model.min_condition,
            min_condition_label=CONDITION_LABELS.get(model.min_condition, 'Unknown'),
            max_price=float(model.max_price) if model.max_price else None,
            status=model.status,
            matched_book_id=model.matched_book_id,
            matched_inventory_id=model.matched_inventory_id,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            expires_at=model.expires_at,
            customer_name=customer_name,
            matched_book_title=matched_book_title,
            is_overdue=model.is_overdue
        )


@dataclass
class BookRequestCreateSchema(BaseSchema):
    """Schema for creating book request."""
    
    customer_id: str  # UUID as string
    title: str
    author: str
    isbn: Optional[str] = None
    min_condition: int = 3
    max_price: Optional[float] = None
    notes: Optional[str] = None
    expiry_days: int = 365
    
    def validate(self) -> list:
        """Validate request data."""
        from app.utils.validators import validate_book_request_data, validate_uuid
        
        errors = []
        
        is_valid, error = validate_uuid(self.customer_id, "Customer ID")
        if not is_valid:
            errors.append(error)
        
        request_errors = validate_book_request_data({
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'min_condition': self.min_condition,
            'max_price': self.max_price
        })
        errors.extend(request_errors)
        
        return errors


@dataclass
class BookRequestUpdateSchema(BaseSchema):
    """Schema for updating book request."""
    
    title: Optional[str] = None
    author: Optional[str] = None
    min_condition: Optional[int] = None
    max_price: Optional[float] = None
    notes: Optional[str] = None
    
    def validate(self) -> list:
        """Validate update data."""
        from app.utils.validators import validate_condition
        
        errors = []
        
        if self.title is not None and not self.title.strip():
            errors.append("Title cannot be empty")
        
        if self.author is not None and not self.author.strip():
            errors.append("Author cannot be empty")
        
        if self.min_condition is not None:
            is_valid, error = validate_condition(self.min_condition)
            if not is_valid:
                errors.append(f"Minimum condition: {error}")
        
        return errors


@dataclass
class BookRequestMatchSchema(BaseSchema):
    """Schema for matching request to inventory."""
    
    book_id: str
    inventory_id: str
    
    def validate(self) -> list:
        """Validate match data."""
        from app.utils.validators import validate_uuid
        
        errors = []
        
        is_valid, error = validate_uuid(self.book_id, "Book ID")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_uuid(self.inventory_id, "Inventory ID")
        if not is_valid:
            errors.append(error)
        
        return errors
