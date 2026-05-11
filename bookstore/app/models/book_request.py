"""
Book Request Domain Model
=========================

Allows customers to request books not currently in inventory.
System matches requests when matching inventory arrives.

Workflow: pending -> matched -> notified -> fulfilled/expired/cancelled
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, Text, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin
from app.extensions import db

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.book import Book
    from app.models.inventory import Inventory


# Request status constants
STATUS_PENDING = 'pending'
STATUS_MATCHED = 'matched'
STATUS_NOTIFIED = 'notified'
STATUS_FULFILLED = 'fulfilled'
STATUS_EXPIRED = 'expired'
STATUS_CANCELLED = 'cancelled'

VALID_STATUSES = [
    STATUS_PENDING, STATUS_MATCHED, STATUS_NOTIFIED,
    STATUS_FULFILLED, STATUS_EXPIRED, STATUS_CANCELLED
]

# Default expiry in days
DEFAULT_EXPIRY_DAYS = 365


class BookRequest(BaseModel, TimestampMixin):
    """
    Customer request for a book not currently in inventory.
    
    Customers can specify:
    - Book details (title, author, optional ISBN)
    - Minimum acceptable condition
    - Maximum price they're willing to pay
    
    When matching inventory arrives, staff can match the request
    and notify the customer.
    
    Attributes:
        customer_id: Customer making the request
        title: Requested book title
        author: Requested author
        isbn: Optional ISBN for precise matching
        min_condition: Minimum acceptable condition (1-5)
        max_price: Maximum price customer will pay
        status: Request workflow status
        matched_book_id: Book that matched (when found)
        matched_inventory_id: Specific inventory item matched
        notes: Customer or staff notes
        expires_at: When request expires
    """
    
    __tablename__ = 'book_requests'
    
    __table_args__ = (
        CheckConstraint(
            f"status IN {tuple(VALID_STATUSES)}",
            name='requests_status_check'
        ),
        CheckConstraint(
            'min_condition BETWEEN 1 AND 5',
            name='requests_condition_check'
        ),
    )
    
    # Customer reference
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('customers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Request details
    isbn: Mapped[Optional[str]] = mapped_column(
        String(17),
        nullable=True,
        index=True
    )
    
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
    
    min_condition: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3
    )
    
    max_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=STATUS_PENDING,
        index=True
    )
    
    # Matching
    matched_book_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('books.id', ondelete='SET NULL'),
        nullable=True
    )
    
    matched_inventory_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('inventory.id', ondelete='SET NULL'),
        nullable=True
    )
    
    # Additional info
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(days=DEFAULT_EXPIRY_DAYS)
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="book_requests",
        lazy="joined"
    )
    
    matched_book: Mapped[Optional["Book"]] = relationship(
        "Book",
        foreign_keys=[matched_book_id],
        lazy="joined"
    )
    
    matched_inventory: Mapped[Optional["Inventory"]] = relationship(
        "Inventory",
        foreign_keys=[matched_inventory_id],
        lazy="joined"
    )
    
    # =========================================================================
    # Status Properties
    # =========================================================================
    
    @property
    def is_pending(self) -> bool:
        return self.status == STATUS_PENDING
    
    @property
    def is_matched(self) -> bool:
        return self.status == STATUS_MATCHED
    
    @property
    def is_notified(self) -> bool:
        return self.status == STATUS_NOTIFIED
    
    @property
    def is_fulfilled(self) -> bool:
        return self.status == STATUS_FULFILLED
    
    @property
    def is_expired(self) -> bool:
        return self.status == STATUS_EXPIRED
    
    @property
    def is_cancelled(self) -> bool:
        return self.status == STATUS_CANCELLED
    
    @property
    def is_active(self) -> bool:
        """Check if request is still active (can be matched)."""
        return self.status in (STATUS_PENDING, STATUS_MATCHED, STATUS_NOTIFIED)
    
    @property
    def is_overdue(self) -> bool:
        """Check if request has passed expiry date."""
        return datetime.utcnow() > self.expires_at
    
    # =========================================================================
    # Condition Label
    # =========================================================================
    
    @property
    def min_condition_label(self) -> str:
        """Get human-readable condition label."""
        from app.models.inventory import CONDITION_LABELS
        return CONDITION_LABELS.get(self.min_condition, 'Unknown')
    
    # =========================================================================
    # Status Transitions
    # =========================================================================
    
    def match(
        self,
        book_id: uuid.UUID,
        inventory_id: uuid.UUID
    ) -> None:
        """
        Match request with found inventory.
        
        Args:
            book_id: Matching book ID
            inventory_id: Matching inventory item ID
        """
        if self.status != STATUS_PENDING:
            raise ValueError(f"Cannot match request in status: {self.status}")
        
        self.matched_book_id = book_id
        self.matched_inventory_id = inventory_id
        self.status = STATUS_MATCHED
    
    def notify_customer(self) -> None:
        """Mark that customer has been notified of match."""
        if self.status != STATUS_MATCHED:
            raise ValueError(f"Cannot notify for request in status: {self.status}")
        self.status = STATUS_NOTIFIED
    
    def fulfill(self) -> None:
        """Mark request as fulfilled (customer purchased)."""
        if self.status not in (STATUS_MATCHED, STATUS_NOTIFIED):
            raise ValueError(f"Cannot fulfill request in status: {self.status}")
        self.status = STATUS_FULFILLED
    
    def expire(self) -> None:
        """Mark request as expired."""
        if self.status not in (STATUS_PENDING, STATUS_MATCHED, STATUS_NOTIFIED):
            raise ValueError(f"Cannot expire request in status: {self.status}")
        self.status = STATUS_EXPIRED
    
    def cancel(self) -> None:
        """Cancel the request."""
        if self.status in (STATUS_FULFILLED, STATUS_CANCELLED):
            raise ValueError(f"Cannot cancel request in status: {self.status}")
        self.status = STATUS_CANCELLED
    
    def unmatch(self) -> None:
        """Remove match (if customer declines or inventory sold)."""
        if self.status not in (STATUS_MATCHED, STATUS_NOTIFIED):
            raise ValueError(f"Cannot unmatch request in status: {self.status}")
        self.matched_book_id = None
        self.matched_inventory_id = None
        self.status = STATUS_PENDING
    
    # =========================================================================
    # Matching Logic
    # =========================================================================
    
    def matches_inventory(self, inventory: "Inventory") -> bool:
        """
        Check if inventory item matches this request.
        
        Args:
            inventory: Inventory item to check
            
        Returns:
            True if inventory matches request criteria
        """
        # Check condition meets minimum
        if inventory.condition < self.min_condition:
            return False
        
        # Check price if max_price specified
        if self.max_price is not None and inventory.list_price > self.max_price:
            return False
        
        # Check if in stock
        if inventory.quantity <= 0:
            return False
        
        # Check title/author match (case-insensitive)
        book = inventory.book
        if not book:
            return False
        
        title_match = self.title.lower() in book.title.lower()
        author_match = self.author.lower() in book.author.lower()
        
        # If ISBN specified, require exact match
        if self.isbn and book.isbn:
            isbn_match = self.isbn.replace('-', '') == book.isbn.replace('-', '')
            return isbn_match and inventory.condition >= self.min_condition
        
        return title_match and author_match
    
    @classmethod
    def find_matching_requests(
        cls,
        book: "Book",
        condition: int,
        price: Decimal
    ) -> list:
        """
        Find pending requests that match new inventory.
        
        Called when new inventory arrives to find customers to notify.
        
        Args:
            book: Book being added to inventory
            condition: Condition grade of new inventory
            price: List price of new inventory
            
        Returns:
            List of matching pending requests
        """
        query = cls.query.filter(
            cls.status == STATUS_PENDING,
            cls.min_condition <= condition,
            cls.expires_at > datetime.utcnow()
        )
        
        # Price filter
        query = query.filter(
            (cls.max_price.is_(None)) | (cls.max_price >= price)
        )
        
        # Title/author matching (case-insensitive)
        # Using ILIKE for PostgreSQL
        query = query.filter(
            db.func.lower(cls.title).contains(db.func.lower(book.title)) |
            db.func.lower(book.title).contains(db.func.lower(cls.title))
        )
        
        return query.all()
    
    @classmethod
    def expire_overdue_requests(cls) -> int:
        """
        Expire all requests past their expiry date.
        
        Returns:
            Number of requests expired
        """
        count = cls.query.filter(
            cls.status.in_([STATUS_PENDING, STATUS_MATCHED, STATUS_NOTIFIED]),
            cls.expires_at < datetime.utcnow()
        ).update({cls.status: STATUS_EXPIRED}, synchronize_session='fetch')
        
        db.session.commit()
        return count
    
    def __repr__(self) -> str:
        return f"<BookRequest '{self.title}' by {self.author} ({self.status})>"
