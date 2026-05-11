"""
Invoice Domain Model
====================

Invoice generation for the rare bookstore.
No online payment processing - invoices are sent and paid externally.

Key features:
- Draft/Sent/Paid/Cancelled workflow
- Line items can be actual inventory or pending book requests
- Auto-generated invoice numbers
"""

import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, Text, ForeignKey, CheckConstraint, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin
from app.extensions import db

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.user import User
    from app.models.book import Book
    from app.models.book_request import BookRequest
    from app.models.inventory import Inventory


# Invoice status constants
STATUS_DRAFT = 'draft'
STATUS_SENT = 'sent'
STATUS_PAID = 'paid'
STATUS_CANCELLED = 'cancelled'

VALID_STATUSES = [STATUS_DRAFT, STATUS_SENT, STATUS_PAID, STATUS_CANCELLED]


class Invoice(BaseModel, TimestampMixin):
    """
    Customer invoice.
    
    Invoices are created as drafts, sent to customers, and marked paid
    when payment is received (payment happens outside the system).
    
    Attributes:
        invoice_number: Unique human-readable invoice number
        customer_id: Customer receiving the invoice
        status: Workflow status (draft/sent/paid/cancelled)
        subtotal: Total amount before any adjustments
        notes: Internal or customer-facing notes
        payment_terms: Payment terms text (e.g., "Net 30")
        created_by: User who created the invoice
    """
    
    __tablename__ = 'invoices'
    
    __table_args__ = (
        CheckConstraint(
            f"status IN {tuple(VALID_STATUSES)}",
            name='invoices_status_check'
        ),
    )
    
    # Invoice identification
    invoice_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Customer reference
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('customers.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    
    # Status workflow
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=STATUS_DRAFT,
        index=True
    )
    
    # Financial
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )
    
    # Additional information
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    payment_terms: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default='Net 30'
    )
    
    # Audit trail
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False
    )
    
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="invoices",
        lazy="joined"
    )
    
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="joined"
    )
    
    lines: Mapped[List["InvoiceLine"]] = relationship(
        "InvoiceLine",
        back_populates="invoice",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="InvoiceLine.created_at"
    )
    
    # =========================================================================
    # Invoice Number Generation
    # =========================================================================
    
    @classmethod
    def generate_invoice_number(cls, prefix: str = 'INV') -> str:
        """
        Generate unique invoice number.
        
        Format: INV-YYYYMMDD-XXXX
        Where XXXX is a sequential counter for that day.
        
        Args:
            prefix: Invoice number prefix
            
        Returns:
            Unique invoice number string
        """
        today = datetime.utcnow().strftime('%Y%m%d')
        
        # Find highest number for today
        from sqlalchemy import func
        pattern = f'{prefix}-{today}-%'
        
        last_invoice = cls.query.filter(
            cls.invoice_number.like(pattern)
        ).order_by(cls.invoice_number.desc()).first()
        
        if last_invoice:
            # Extract sequence number and increment
            seq = int(last_invoice.invoice_number.split('-')[-1]) + 1
        else:
            seq = 1
        
        return f"{prefix}-{today}-{seq:04d}"
    
    # =========================================================================
    # Status Workflow
    # =========================================================================
    
    @property
    def is_draft(self) -> bool:
        return self.status == STATUS_DRAFT
    
    @property
    def is_sent(self) -> bool:
        return self.status == STATUS_SENT
    
    @property
    def is_paid(self) -> bool:
        return self.status == STATUS_PAID
    
    @property
    def is_cancelled(self) -> bool:
        return self.status == STATUS_CANCELLED
    
    @property
    def can_edit(self) -> bool:
        """Check if invoice can be edited (only drafts)."""
        return self.status == STATUS_DRAFT
    
    @property
    def can_send(self) -> bool:
        """Check if invoice can be sent."""
        return self.status == STATUS_DRAFT and self.line_count > 0
    
    @property
    def can_mark_paid(self) -> bool:
        """Check if invoice can be marked as paid."""
        return self.status == STATUS_SENT
    
    @property
    def can_cancel(self) -> bool:
        """Check if invoice can be cancelled."""
        return self.status in (STATUS_DRAFT, STATUS_SENT)
    
    def send(self) -> None:
        """Mark invoice as sent."""
        if not self.can_send:
            raise ValueError(f"Cannot send invoice in status: {self.status}")
        self.status = STATUS_SENT
        self.sent_at = datetime.utcnow()
    
    def mark_paid(self) -> None:
        """Mark invoice as paid."""
        if not self.can_mark_paid:
            raise ValueError(f"Cannot mark as paid invoice in status: {self.status}")
        self.status = STATUS_PAID
        self.paid_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancel invoice."""
        if not self.can_cancel:
            raise ValueError(f"Cannot cancel invoice in status: {self.status}")
        self.status = STATUS_CANCELLED
    
    # =========================================================================
    # Line Item Management
    # =========================================================================
    
    @property
    def line_count(self) -> int:
        """Get number of line items."""
        return self.lines.count()
    
    @property
    def has_pending_items(self) -> bool:
        """Check if invoice has any pending (request) items."""
        return self.lines.filter_by(is_pending=True).count() > 0
    
    def recalculate_subtotal(self) -> Decimal:
        """Recalculate subtotal from line items."""
        from sqlalchemy import func
        result = self.lines.filter(
            InvoiceLine.unit_price.isnot(None)
        ).with_entities(
            func.sum(InvoiceLine.quantity * InvoiceLine.unit_price)
        ).scalar()
        
        self.subtotal = Decimal(result) if result else Decimal(0)
        return self.subtotal
    
    def add_line(
        self,
        description: str,
        quantity: int = 1,
        unit_price: Optional[Decimal] = None,
        book_id: Optional[uuid.UUID] = None,
        inventory_id: Optional[uuid.UUID] = None,
        request_id: Optional[uuid.UUID] = None,
        condition: Optional[int] = None
    ) -> "InvoiceLine":
        """
        Add a line item to the invoice.
        
        Args:
            description: Line item description
            quantity: Number of items
            unit_price: Price per item (None for pending items)
            book_id: Optional book reference
            inventory_id: Optional inventory reference
            request_id: Optional book request reference
            condition: Book condition grade
            
        Returns:
            Created InvoiceLine
        """
        if not self.can_edit:
            raise ValueError("Cannot add lines to non-draft invoice")
        
        line_type = 'request' if request_id else 'item'
        is_pending = request_id is not None
        
        line = InvoiceLine(
            invoice_id=self.id,
            line_type=line_type,
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            book_id=book_id,
            inventory_id=inventory_id,
            request_id=request_id,
            condition=condition,
            is_pending=is_pending
        )
        
        db.session.add(line)
        db.session.flush()
        
        self.recalculate_subtotal()
        return line
    
    def __repr__(self) -> str:
        return f"<Invoice {self.invoice_number} ({self.status})>"


class InvoiceLine(BaseModel):
    """
    Invoice line item.
    
    Can represent either:
    - An actual inventory item (line_type='item')
    - A pending book request (line_type='request', is_pending=True)
    
    Attributes:
        invoice_id: Parent invoice
        line_type: 'item' or 'request'
        description: Line item description
        quantity: Number of items
        unit_price: Price per item (None for pending)
        condition: Book condition grade
        is_pending: Whether this is a pending request
    """
    
    __tablename__ = 'invoice_lines'
    
    __table_args__ = (
        CheckConstraint(
            "line_type IN ('item', 'request')",
            name='lines_type_check'
        ),
    )
    
    # Parent reference
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('invoices.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    line_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default='item'
    )
    
    # Item references (one of these should be set)
    book_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('books.id', ondelete='SET NULL'),
        nullable=True
    )
    
    inventory_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('inventory.id', ondelete='SET NULL'),
        nullable=True
    )
    
    request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('book_requests.id', ondelete='SET NULL'),
        nullable=True
    )
    
    # Line item details
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    condition: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )
    
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    
    is_pending: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    invoice: Mapped["Invoice"] = relationship(
        "Invoice",
        back_populates="lines"
    )
    
    book: Mapped[Optional["Book"]] = relationship(
        "Book",
        lazy="joined"
    )
    
    inventory: Mapped[Optional["Inventory"]] = relationship(
        "Inventory",
        lazy="joined"
    )
    
    request: Mapped[Optional["BookRequest"]] = relationship(
        "BookRequest",
        lazy="joined"
    )
    
    # =========================================================================
    # Computed Properties
    # =========================================================================
    
    @property
    def line_total(self) -> Optional[Decimal]:
        """Calculate line total (quantity * unit_price)."""
        if self.unit_price is None:
            return None
        return Decimal(self.quantity) * Decimal(self.unit_price)
    
    @property
    def condition_label(self) -> str:
        """Get human-readable condition label."""
        from app.models.inventory import CONDITION_LABELS
        if self.condition is None:
            return 'N/A'
        return CONDITION_LABELS.get(self.condition, 'Unknown')
    
    def __repr__(self) -> str:
        return f"<InvoiceLine {self.description[:30]}... qty={self.quantity}>"
