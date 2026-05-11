"""
Base Model Classes
==================

Provides base classes and mixins for all domain models.
Implements common functionality like timestamps, soft deletes, and UUID keys.

Design Pattern: Template Method Pattern
- Base classes define common structure
- Concrete models override/extend as needed
"""

import uuid
from datetime import datetime
from typing import Optional, Any, Dict

from sqlalchemy import Boolean, DateTime, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

from app.extensions import db


class TimestampMixin:
    """
    Mixin providing created_at and updated_at timestamps.
    
    Automatically sets created_at on insert and updated_at on update.
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class SoftDeleteMixin:
    """
    Mixin providing soft delete functionality.
    
    Records are marked inactive instead of being physically deleted.
    Preserves audit trail and allows recovery.
    """
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    def soft_delete(self) -> None:
        """Mark record as inactive (soft delete)."""
        self.is_active = False
    
    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_active = True


class UUIDMixin:
    """
    Mixin providing UUID primary key.
    
    UUIDs prevent ID enumeration attacks and work well in distributed systems.
    """
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


class BaseModel(db.Model, UUIDMixin, TimestampMixin):
    """
    Abstract base model with UUID primary key and timestamps.
    
    All domain models should inherit from this class.
    Provides common functionality for serialization and comparison.
    """
    
    __abstract__ = True
    
    def to_dict(self, exclude: Optional[set] = None) -> Dict[str, Any]:
        """
        Convert model to dictionary for serialization.
        
        Args:
            exclude: Set of field names to exclude from output
            
        Returns:
            Dictionary representation of the model
        """
        exclude = exclude or set()
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                # Handle UUID serialization
                if isinstance(value, uuid.UUID):
                    value = str(value)
                # Handle datetime serialization
                elif isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value
        
        return result
    
    def update_from_dict(self, data: Dict[str, Any], exclude: Optional[set] = None) -> None:
        """
        Update model fields from dictionary.
        
        Args:
            data: Dictionary with field values
            exclude: Set of field names to exclude from update
        """
        exclude = exclude or {'id', 'created_at', 'updated_at'}
        
        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<{self.__class__.__name__} id={self.id}>"


class AuditableModel(BaseModel, SoftDeleteMixin):
    """
    Base model with soft delete capability.
    
    Use for entities that should preserve history (books, customers, etc.)
    """
    
    __abstract__ = True
