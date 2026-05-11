"""
Inventory Domain Model
======================

Tracks physical book copies with condition grades across warehouses.
Separate from Book model which represents catalog entries.

Key design: Same book in different conditions = different inventory records.
"""

import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Integer, Numeric, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin
from app.extensions import db

if TYPE_CHECKING:
    from app.models.book import Book


# Condition grade constants
CONDITION_FINE = 5
CONDITION_VERY_GOOD = 4
CONDITION_GOOD = 3
CONDITION_FAIR = 2
CONDITION_POOR = 1

CONDITION_LABELS = {
    CONDITION_FINE: 'Fine',
    CONDITION_VERY_GOOD: 'Very Good',
    CONDITION_GOOD: 'Good',
    CONDITION_FAIR: 'Fair',
    CONDITION_POOR: 'Poor'
}


class Warehouse(BaseModel):
    """
    Physical storage location for inventory.
    
    Attributes:
        name: Warehouse name
        location: Address or location description
        capacity: Maximum item capacity
    """
    
    __tablename__ = 'warehouses'
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    capacity: Mapped[int] = mapped_column(
        Integer,
        default=10000,
        nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False
    )
    
    # Relationships
    inventory_items: Mapped[List["Inventory"]] = relationship(
        "Inventory",
        back_populates="warehouse",
        lazy="dynamic"
    )
    
    def get_total_items(self) -> int:
        """Get total items in this warehouse."""
        from sqlalchemy import func
        result = Inventory.query.filter_by(
            warehouse_id=self.id
        ).with_entities(func.sum(Inventory.quantity)).scalar()
        return int(result) if result else 0
    
    def get_utilization(self) -> float:
        """Get capacity utilization as percentage."""
        if self.capacity == 0:
            return 0.0
        return (self.get_total_items() / self.capacity) * 100
    
    def __repr__(self) -> str:
        return f"<Warehouse {self.name}>"


class Inventory(BaseModel, TimestampMixin):
    """
    Inventory record for a book in a specific condition at a warehouse.
    
    Unique constraint: One record per (book, warehouse, condition) combination.
    
    Attributes:
        book_id: Reference to book catalog entry
        warehouse_id: Reference to storage location
        condition: Condition grade (1-5)
        quantity: Number of copies
        acquisition_cost: Cost to acquire (for profit calculation)
        list_price: Selling price
        reorder_level: Threshold for low-stock alerts
        location_code: Shelf/bin location within warehouse
    """
    
    __tablename__ = 'inventory'
    
    __table_args__ = (
        UniqueConstraint('book_id', 'warehouse_id', 'condition', name='inventory_unique'),
        CheckConstraint('condition BETWEEN 1 AND 5', name='inventory_condition_check'),
        CheckConstraint('quantity >= 0', name='inventory_quantity_check'),
    )
    
    # Foreign keys
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('books.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('warehouses.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    
    # Condition (1-5 scale)
    condition: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )
    
    # Quantity and pricing
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    
    acquisition_cost: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    
    list_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    
    # Stock management
    reorder_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    
    location_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="inventory_items",
        lazy="joined"
    )
    
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse",
        back_populates="inventory_items",
        lazy="joined"
    )
    
    # =========================================================================
    # Business Logic
    # =========================================================================
    
    @property
    def condition_label(self) -> str:
        """Get human-readable condition label."""
        return CONDITION_LABELS.get(self.condition, 'Unknown')
    
    @property
    def is_low_stock(self) -> bool:
        """Check if inventory is at or below reorder level."""
        return self.quantity <= self.reorder_level
    
    @property
    def is_out_of_stock(self) -> bool:
        """Check if inventory is empty."""
        return self.quantity == 0
    
    @property
    def profit_margin(self) -> float:
        """Calculate profit margin percentage."""
        if self.acquisition_cost == 0:
            return 100.0
        return ((self.list_price - self.acquisition_cost) / self.list_price) * 100
    
    def adjust_quantity(self, delta: int, reason: str = None) -> int:
        """
        Adjust inventory quantity by delta (positive or negative).
        
        Args:
            delta: Amount to add (positive) or remove (negative)
            reason: Optional reason for adjustment
            
        Returns:
            New quantity after adjustment
            
        Raises:
            ValueError: If adjustment would result in negative quantity
        """
        new_quantity = self.quantity + delta
        if new_quantity < 0:
            raise ValueError(
                f"Insufficient inventory: have {self.quantity}, need {abs(delta)}"
            )
        self.quantity = new_quantity
        return new_quantity
    
    def reserve(self, quantity: int) -> bool:
        """
        Reserve inventory for a sale (reduce quantity).
        
        Args:
            quantity: Number of items to reserve
            
        Returns:
            True if reservation successful
            
        Raises:
            ValueError: If insufficient quantity
        """
        if quantity > self.quantity:
            raise ValueError(
                f"Cannot reserve {quantity}: only {self.quantity} available"
            )
        self.quantity -= quantity
        return True
    
    def restock(self, quantity: int, unit_cost: Optional[float] = None) -> int:
        """
        Add inventory from purchase order receipt.
        
        Args:
            quantity: Number of items to add
            unit_cost: Optional new acquisition cost (updates average)
            
        Returns:
            New quantity after restock
        """
        if unit_cost is not None:
            # Calculate weighted average cost
            total_cost = (self.quantity * self.acquisition_cost) + (quantity * unit_cost)
            total_qty = self.quantity + quantity
            self.acquisition_cost = total_cost / total_qty if total_qty > 0 else unit_cost
        
        self.quantity += quantity
        return self.quantity
    
    # =========================================================================
    # Class Methods
    # =========================================================================
    
    @classmethod
    def get_low_stock_items(cls) -> List["Inventory"]:
        """Get all inventory items at or below reorder level."""
        return cls.query.filter(
            cls.quantity <= cls.reorder_level,
            cls.quantity > 0
        ).all()
    
    @classmethod
    def get_out_of_stock_items(cls) -> List["Inventory"]:
        """Get all out-of-stock inventory items."""
        return cls.query.filter(cls.quantity == 0).all()
    
    def __repr__(self) -> str:
        book_title = self.book.short_title if self.book else 'Unknown'
        return f"<Inventory {book_title} ({self.condition_label}): {self.quantity}>"
