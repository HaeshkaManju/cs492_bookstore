"""
User Schemas
============

DTOs for user-related API operations.
"""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.schemas.base import BaseSchema, parse_uuid, parse_datetime


@dataclass
class UserSchema(BaseSchema):
    """Schema for user responses."""
    
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def from_model(cls, model) -> 'UserSchema':
        return cls(
            id=model.id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )


@dataclass
class UserCreateSchema(BaseSchema):
    """Schema for user creation requests."""
    
    email: str
    password: str
    first_name: str
    last_name: str
    role: str = 'customer'
    
    def validate(self) -> list:
        """Validate input data."""
        from app.utils.validators import (
            validate_email, validate_password, validate_name
        )
        
        errors = []
        
        is_valid, error = validate_email(self.email)
        if not is_valid:
            errors.append(f"Email: {error}")
        
        is_valid, error = validate_password(self.password)
        if not is_valid:
            errors.append(f"Password: {error}")
        
        is_valid, error = validate_name(self.first_name, "First name")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_name(self.last_name, "Last name")
        if not is_valid:
            errors.append(error)
        
        if self.role not in ('admin', 'employee', 'customer'):
            errors.append(f"Invalid role: {self.role}")
        
        return errors


@dataclass
class UserUpdateSchema(BaseSchema):
    """Schema for user update requests."""
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    
    def validate(self) -> list:
        """Validate input data."""
        from app.utils.validators import validate_email, validate_name
        
        errors = []
        
        if self.email is not None:
            is_valid, error = validate_email(self.email)
            if not is_valid:
                errors.append(f"Email: {error}")
        
        if self.first_name is not None:
            is_valid, error = validate_name(self.first_name, "First name")
            if not is_valid:
                errors.append(error)
        
        if self.last_name is not None:
            is_valid, error = validate_name(self.last_name, "Last name")
            if not is_valid:
                errors.append(error)
        
        if self.role is not None and self.role not in ('admin', 'employee', 'customer'):
            errors.append(f"Invalid role: {self.role}")
        
        return errors


@dataclass
class PasswordChangeSchema(BaseSchema):
    """Schema for password change requests."""
    
    current_password: str
    new_password: str
    confirm_password: str
    
    def validate(self) -> list:
        """Validate input data."""
        from app.utils.validators import validate_password, validate_password_match
        
        errors = []
        
        is_valid, error = validate_password(self.new_password)
        if not is_valid:
            errors.append(f"New password: {error}")
        
        is_valid, error = validate_password_match(self.new_password, self.confirm_password)
        if not is_valid:
            errors.append(error)
        
        return errors
