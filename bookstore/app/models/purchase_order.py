"""
Purchase Order Domain Model
===========================

Manages orders to book manufacturers/suppliers.
Tracks order lifecycle from draft through receipt.

When POs are received, inventory is automatically updated.
"""

import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, Text, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, AuditableModel, TimestampMixin
from app.extensions import db

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.book import Book


# PO status constants
STATUS_DRAFT = 'draft'
STATUS_SUBMITTED = 'submitted'
STATUS_CONFIRMED = 'confirmed'
STATUS_SHIPPED = 'shipped'
STATUS_RECEIVED = 'received'
STATUS_CANCELLED = 'cancelled'

VALID_STATUSES = [
    STATUS_DRAFT, STATUS_SUBMITTED, STATUS_CONFIRMED,
    STATUS_SHIPPED, STATUS_RECEIVED, STATUS_CANCELLED
]


class Manufacturer(AuditableModel):
    """
    Book manufacturer/supplier.
    
    Attributes:
        name: Company name
        contact_name: Primary contact person
        email: Contact email
        phone: Contact phone
        address: Mailing address
    """
    
    __tablename__ = 'manufacturers'
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    
    contact_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    address: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship(
        "PurchaseOrder",
        back_populates="manufacturer",
        lazy="dynamic"
    )
    
    def __repr__(self) -> str:
        return f"<Manufacturer {self.name}>"


class PurchaseOrder(BaseModel, TimestampMixin):
    """
    Purchase order to a manufacturer.
    
    Workflow: draft -> submitted -> confirmed -> shipped -> received
    Can be cancelled at any point before received.
    
    Attributes:
        po_number: Unique human-readable PO number
        manufacturer_id: Supplier for this order
        status: Workflow status
        total: Total order amount
        notes: Order notes
        created_by: User who created the PO
    """
    
    __tablename__ = 'purchase_orders'
    
    __table_args__ = (
        CheckConstraint(
            f"status IN {tuple(VALID_STATUSES)}",
            name='po_status_check'
        ),
    )
    
    # PO identification
    po_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Manufacturer reference
    manufacturer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('manufacturers.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=STATUS_DRAFT,
        index=True
    )
    
    # Financial
    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )
    
    # Additional info
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Audit trail
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False
    )
    
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    
    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    manufacturer: Mapped["Manufacturer"] = relationship(
        "Manufacturer",
        back_populates="purchase_orders",
        lazy="joined"
    )
    
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="joined"
    )
    
    lines: Mapped[List["POLine"]] = relationship(
        "POLine",
        back_populates="purchase_order",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="POLine.created_at"
    )
    
    # =========================================================================
    # PO Number Generation
    # =========================================================================
    
    @classmethod
    def generate_po_number(cls, prefix: str = 'PO') -> str:
        """
        Generate unique PO number.
        
        Format: PO-YYYYMMDD-XXXX
        
        Args:
            prefix: PO number prefix
            
        Returns:
            Unique PO number string
        """
        today = datetime.utcnow().strftime('%Y%m%d')
        
        from sqlalchemy import func
        pattern = f'{prefix}-{today}-%'
        
        last_po = cls.query.filter(
            cls.po_number.like(pattern)
        ).order_by(cls.po_number.desc()).first()
        
        if last_po:
            seq = int(last_po.po_number.split('-')[-1]) + 1
        else:
            seq = 1
        
        return f"{prefix}-{today}-{seq:04d}"
    
    # =========================================================================
    # Status Properties
    # =========================================================================
    
    @property
    def is_draft(self) -> bool:
        return self.status == STATUS_DRAFT
    
    @property
    def is_submitted(self) -> bool:
        return self.status == STATUS_SUBMITTED
    
    @property
    def is_confirmed(self) -> bool:
        return self.status == STATUS_CONFIRMED
    
    @property
    def is_shipped(self) -> bool:
        return self.status == STATUS_SHIPPED
    
    @property
    def is_received(self) -> bool:
        return self.status == STATUS_RECEIVED
    
    @property
    def is_cancelled(self) -> bool:
        return self.status == STATUS_CANCELLED
    
    @property
    def can_edit(self) -> bool:
        """Check if PO can be edited."""
        return self.status == STATUS_DRAFT
    
    @property
    def can_submit(self) -> bool:
        """Check if PO can be submitted."""
        return self.status == STATUS_DRAFT and self.line_count > 0
    
    @property
    def can_receive(self) -> bool:
        """Check if PO can be received."""
        return self.status in (STATUS_SUBMITTED, STATUS_CONFIRMED, STATUS_SHIPPED)
    
    @property
    def can_cancel(self) -> bool:
        """Check if PO can be cancelled."""
        return self.status not in (STATUS_RECEIVED, STATUS_CANCELLED)
    
    # =========================================================================
    # Status Transitions
    # =========================================================================
    
    def submit(self) -> None:
        """Submit PO to manufacturer."""
        if not self.can_submit:
            raise ValueError(f"Cannot submit PO in status: {self.status}")
        self.status = STATUS_SUBMITTED
        self.submitted_at = datetime.utcnow()
    
    def confirm(self) -> None:
        """Mark PO as confirmed by manufacturer."""
        if self.status != STATUS_SUBMITTED:
            raise ValueError(f"Cannot confirm PO in status: {self.status}")
        self.status = STATUS_CONFIRMED
    
    def mark_shipped(self) -> None:
        """Mark PO as shipped."""
        if self.status != STATUS_CONFIRMED:
            raise ValueError(f"Cannot mark shipped PO in status: {self.status}")
        self.status = STATUS_SHIPPED
    
    def receive(self) -> None:
        """
        Mark PO as received.
        
        Note: Actual inventory updates should be handled by the service layer
        when calling this method.
        """
        if not self.can_receive:
            raise ValueError(f"Cannot receive PO in status: {self.status}")
        self.status = STATUS_RECEIVED
        self.received_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancel the PO."""
        if not self.can_cancel:
            raise ValueError(f"Cannot cancel PO in status: {self.status}")
        self.status = STATUS_CANCELLED
    
    # =========================================================================
    # Line Management
    # =========================================================================
    
    @property
    def line_count(self) -> int:
        """Get number of line items."""
        return self.lines.count()
    
    @property
    def total_items_ordered(self) -> int:
        """Get total quantity of items ordered."""
        from sqlalchemy import func
        result = self.lines.with_entities(func.sum(POLine.quantity)).scalar()
        return int(result) if result else 0
    
    @property
    def total_items_received(self) -> int:
        """Get total quantity of items received."""
        from sqlalchemy import func
        result = self.lines.with_entities(func.sum(POLine.received_qty)).scalar()
        return int(result) if result else 0
    
    @property
    def is_fully_received(self) -> bool:
        """Check if all ordered items have been received."""
        return self.total_items_received >= self.total_items_ordered
    
    def recalculate_total(self) -> Decimal:
        """Recalculate total from line items."""
        from sqlalchemy import func
        result = self.lines.with_entities(
            func.sum(POLine.quantity * POLine.unit_cost)
        ).scalar()
        
        self.total = Decimal(result) if result else Decimal(0)
        return self.total
    
    def add_line(
        self,
        description: str,
        quantity: int,
        unit_cost: Decimal,
        book_id: Optional[uuid.UUID] = None,
        isbn: Optional[str] = None,
        expected_condition: Optional[int] = None
    ) -> "POLine":
        """
        Add a line item to the PO.
        
        Args:
            description: Line item description
            quantity: Number of items to order
            unit_cost: Cost per item
            book_id: Optional book reference
            isbn: Optional ISBN for ordering
            expected_condition: Expected condition grade
            
        Returns:
            Created POLine
        """
        if not self.can_edit:
            raise ValueError("Cannot add lines to non-draft PO")
        
        line = POLine(
            po_id=self.id,
            book_id=book_id,
            description=description,
            isbn=isbn,
            expected_condition=expected_condition,
            quantity=quantity,
            unit_cost=unit_cost
        )
        
        db.session.add(line)
        db.session.flush()
        
        self.recalculate_total()
        return line
    
    def __repr__(self) -> str:
        return f"<PurchaseOrder {self.po_number} ({self.status})>"


class POLine(BaseModel, TimestampMixin):
    """
    Purchase order line item.
    
    Attributes:
        po_id: Parent purchase order
        book_id: Optional book reference (for existing books)
        description: Item description
        isbn: ISBN for ordering
        expected_condition: Expected condition grade
        quantity: Quantity ordered
        unit_cost: Cost per item
        received_qty: Quantity actually received
    """
    
    __tablename__ = 'po_lines'
    
    # Parent reference
    po_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('purchase_orders.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Book reference (optional - may be ordering new title)
    book_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('books.id', ondelete='SET NULL'),
        nullable=True
    )
    
    # Line item details
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    isbn: Mapped[Optional[str]] = mapped_column(
        String(17),
        nullable=True
    )
    
    expected_condition: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )
    
    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    
    received_qty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    purchase_order: Mapped["PurchaseOrder"] = relationship(
        "PurchaseOrder",
        back_populates="lines"
    )
    
    book: Mapped[Optional["Book"]] = relationship(
        "Book",
        lazy="joined"
    )
    
    # =========================================================================
    # Computed Properties
    # =========================================================================
    
    @property
    def line_total(self) -> Decimal:
        """Calculate line total (quantity * unit_cost)."""
        return Decimal(self.quantity) * Decimal(self.unit_cost)
    
    @property
    def is_fully_received(self) -> bool:
        """Check if all ordered quantity has been received."""
        return self.received_qty >= self.quantity
    
    @property
    def pending_qty(self) -> int:
        """Get quantity still pending receipt."""
        return max(0, self.quantity - self.received_qty)
    
    @property
    def condition_label(self) -> str:
        """Get human-readable condition label."""
        from app.models.inventory import CONDITION_LABELS
        if self.expected_condition is None:
            return 'N/A'
        return CONDITION_LABELS.get(self.expected_condition, 'Unknown')
    
    def receive(self, quantity: int) -> int:
        """
        Record receipt of items.
        
        Args:
            quantity: Number of items received
            
        Returns:
            New total received quantity
        """
        self.received_qty += quantity
        return self.received_qty
    
    def __repr__(self) -> str:
        return f"<POLine {self.description[:30]}... qty={self.quantity}>"
