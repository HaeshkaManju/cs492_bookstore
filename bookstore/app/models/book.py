"""
Book Domain Model
=================

Represents book catalog entries (titles/editions, not individual copies).
Individual copies with condition are tracked in Inventory model.

This is a core entity in the system - many other modules reference books.
"""

import uuid
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditableModel

if TYPE_CHECKING:
    from app.models.inventory import Inventory


class Book(AuditableModel):
    """
    Book catalog entry.
    
    Represents a book title/edition, not a specific physical copy.
    Physical copies with condition grades are tracked in Inventory.
    
    Attributes:
        isbn: ISBN-10 or ISBN-13 (optional for rare books)
        title: Book title
        author: Author name(s)
        publisher: Publisher name
        year_published: Publication year
        description: Book description/synopsis
        category: Genre or category
    """
    
    __tablename__ = 'books'
    
    # Identification
    isbn: Mapped[Optional[str]] = mapped_column(
        String(17),
        nullable=True,
        index=True
    )
    
    # Core information
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True
    )
    
    author: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    
    publisher: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    year_published: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Extended information
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    inventory_items: Mapped[List["Inventory"]] = relationship(
        "Inventory",
        back_populates="book",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    
    # =========================================================================
    # Inventory Queries
    # =========================================================================
    
    def get_total_quantity(self) -> int:
        """Get total quantity across all warehouses and conditions."""
        from app.models.inventory import Inventory
        from sqlalchemy import func
        
        result = Inventory.query.filter_by(
            book_id=self.id
        ).with_entities(func.sum(Inventory.quantity)).scalar()
        
        return int(result) if result else 0
    
    def get_available_conditions(self) -> List[dict]:
        """
        Get list of available conditions with quantities and prices.
        
        Returns:
            List of dicts with condition, quantity, price info
        """
        from app.models.inventory import Inventory
        from sqlalchemy import func
        
        results = Inventory.query.filter(
            Inventory.book_id == self.id,
            Inventory.quantity > 0
        ).with_entities(
            Inventory.condition,
            func.sum(Inventory.quantity).label('total_qty'),
            func.min(Inventory.list_price).label('min_price')
        ).group_by(Inventory.condition).order_by(Inventory.condition.desc()).all()
        
        condition_labels = {5: 'Fine', 4: 'Very Good', 3: 'Good', 2: 'Fair', 1: 'Poor'}
        
        return [
            {
                'condition': r.condition,
                'condition_label': condition_labels.get(r.condition, 'Unknown'),
                'quantity': int(r.total_qty),
                'min_price': float(r.min_price)
            }
            for r in results
        ]
    
    def get_lowest_price(self) -> Optional[float]:
        """Get lowest available price for this book."""
        from app.models.inventory import Inventory
        from sqlalchemy import func
        
        result = Inventory.query.filter(
            Inventory.book_id == self.id,
            Inventory.quantity > 0
        ).with_entities(func.min(Inventory.list_price)).scalar()
        
        return float(result) if result else None
    
    def is_in_stock(self) -> bool:
        """Check if book has any copies in stock."""
        return self.get_total_quantity() > 0
    
    # =========================================================================
    # Display Methods
    # =========================================================================
    
    @property
    def short_title(self) -> str:
        """Return truncated title for display."""
        if len(self.title) > 50:
            return self.title[:47] + '...'
        return self.title
    
    @property
    def citation(self) -> str:
        """Return formatted citation string."""
        parts = [self.author, f'"{self.title}"']
        if self.publisher:
            parts.append(self.publisher)
        if self.year_published:
            parts.append(str(self.year_published))
        return ', '.join(parts)
    
    def __repr__(self) -> str:
        return f"<Book '{self.short_title}' by {self.author}>"
