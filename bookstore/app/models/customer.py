"""
Customer Domain Model
=====================

Extended profile for customer users with business-specific data.
Separates customer concerns from authentication (User model).

Design: Composition over inheritance
- Customer HAS-A User (composition via foreign key)
- Allows non-customer users without customer profiles
"""

import uuid
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditableModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.address import Address
    from app.models.invoice import Invoice
    from app.models.book_request import BookRequest


class Customer(AuditableModel):
    """
    Customer profile extending User with business data.
    
    Stores customer-specific information like company, payment terms,
    and has relationships to invoices and book requests.
    
    Attributes:
        user_id: Link to User account
        company_name: Optional company/organization name
        phone: Contact phone number
        notes: Internal notes about customer
        credit_terms: Payment terms (e.g., "Net 30")
    """
    
    __tablename__ = 'customers'
    
    # Link to User account
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        unique=True,
        nullable=False
    )
    
    # Business information
    company_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    credit_terms: Mapped[str] = mapped_column(
        String(50),
        default='Net 30',
        nullable=False
    )
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="customer",
        lazy="joined"
    )
    
    addresses: Mapped[List["Address"]] = relationship(
        "Address",
        back_populates="customer",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    
    invoices: Mapped[List["Invoice"]] = relationship(
        "Invoice",
        back_populates="customer",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    
    book_requests: Mapped[List["BookRequest"]] = relationship(
        "BookRequest",
        back_populates="customer",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    
    # =========================================================================
    # Convenience Properties
    # =========================================================================
    
    @property
    def email(self) -> str:
        """Get customer's email from linked User."""
        return self.user.email if self.user else None
    
    @property
    def full_name(self) -> str:
        """Get customer's full name from linked User."""
        return self.user.full_name if self.user else None
    
    @property
    def display_name(self) -> str:
        """Get display name (company or personal name)."""
        if self.company_name:
            return self.company_name
        return self.full_name
    
    @property
    def primary_address(self) -> Optional["Address"]:
        """Get primary billing address."""
        from app.models.address import Address
        return Address.query.filter_by(
            customer_id=self.id,
            is_primary=True
        ).first()
    
    # =========================================================================
    # Business Methods
    # =========================================================================
    
    def get_pending_requests_count(self) -> int:
        """Count pending book requests."""
        from app.models.book_request import BookRequest
        return BookRequest.query.filter_by(
            customer_id=self.id,
            status='pending'
        ).count()
    
    def get_unpaid_invoices_total(self) -> float:
        """Calculate total of unpaid invoices."""
        from app.models.invoice import Invoice
        from sqlalchemy import func
        
        result = Invoice.query.filter_by(
            customer_id=self.id,
            status='sent'
        ).with_entities(func.sum(Invoice.subtotal)).scalar()
        
        return float(result) if result else 0.0
    
    def __repr__(self) -> str:
        return f"<Customer {self.display_name}>"


class Address(AuditableModel):
    """
    Customer address (billing or shipping).
    
    Supports multiple addresses per customer with primary flag.
    """
    
    __tablename__ = 'addresses'
    
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('customers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    address_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='billing'
    )
    
    street: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    zip_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    
    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default='USA'
    )
    
    is_primary: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )
    
    # Relationship
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="addresses"
    )
    
    @property
    def formatted(self) -> str:
        """Return formatted address string."""
        parts = [self.street, f"{self.city}, {self.state} {self.zip_code}"]
        if self.country != 'USA':
            parts.append(self.country)
        return '\n'.join(parts)
    
    def __repr__(self) -> str:
        return f"<Address {self.address_type}: {self.city}, {self.state}>"
