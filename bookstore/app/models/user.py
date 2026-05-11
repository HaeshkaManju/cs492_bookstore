"""
User Domain Model
=================

Handles user accounts and authentication data.
Separate from Customer profile which extends user with business data.

Note: RBAC (role checks, permissions) will be handled by another team member.
This module focuses on user data storage and password management.
"""

import uuid
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app.models.base import AuditableModel

if TYPE_CHECKING:
    from app.models.customer import Customer


class User(AuditableModel, UserMixin):
    """
    User account model for authentication.
    
    Stores credentials and basic identity information.
    Extended by Customer model for customer-specific data.
    
    Attributes:
        email: Unique email address (used for login)
        password_hash: Bcrypt-hashed password
        role: User role (admin, employee, customer)
        first_name: User's first name
        last_name: User's last name
        is_active: Whether account is active (soft delete)
    """
    
    __tablename__ = 'users'
    
    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Role (RBAC integration point - another team member will add decorators)
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='customer',
        index=True
    )
    
    # Identity
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    # Relationships
    customer: Mapped[Optional["Customer"]] = relationship(
        "Customer",
        back_populates="user",
        uselist=False,
        lazy="joined"
    )
    
    # =========================================================================
    # Password Management
    # =========================================================================
    
    def set_password(self, password: str) -> None:
        """
        Hash and store password.
        
        Uses werkzeug's PBKDF2 with SHA256 (secure default).
        For production, consider using bcrypt for adjustable work factor.
        
        Args:
            password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=16
        )
    
    def check_password(self, password: str) -> bool:
        """
        Verify password against stored hash.
        
        Uses constant-time comparison to prevent timing attacks.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    # =========================================================================
    # Flask-Login Integration
    # =========================================================================
    
    def get_id(self) -> str:
        """Return user ID as string for Flask-Login."""
        return str(self.id)
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (required by Flask-Login)."""
        return True
    
    @property
    def is_anonymous(self) -> bool:
        """Check if user is anonymous (required by Flask-Login)."""
        return False
    
    # =========================================================================
    # Convenience Properties
    # =========================================================================
    
    @property
    def full_name(self) -> str:
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == 'admin'
    
    @property
    def is_employee(self) -> bool:
        """Check if user has employee role."""
        return self.role == 'employee'
    
    @property
    def is_customer(self) -> bool:
        """Check if user has customer role."""
        return self.role == 'customer'
    
    @property
    def is_staff(self) -> bool:
        """Check if user is admin or employee."""
        return self.role in ('admin', 'employee')
    
    # =========================================================================
    # Serialization
    # =========================================================================
    
    def to_dict(self, exclude: set = None) -> dict:
        """Convert to dict, excluding password hash by default."""
        exclude = exclude or set()
        exclude.add('password_hash')
        return super().to_dict(exclude)
    
    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
