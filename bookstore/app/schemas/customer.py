"""
Customer Schemas
================

DTOs for customer-related API operations.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.schemas.base import BaseSchema, parse_uuid


@dataclass
class AddressSchema(BaseSchema):
    """Schema for address data."""
    
    id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    address_type: str = 'billing'
    street: str = ''
    city: str = ''
    state: Optional[str] = None
    zip_code: str = ''
    country: str = 'USA'
    is_primary: bool = False
    
    @classmethod
    def from_model(cls, model) -> 'AddressSchema':
        return cls(
            id=model.id,
            customer_id=model.customer_id,
            address_type=model.address_type,
            street=model.street,
            city=model.city,
            state=model.state,
            zip_code=model.zip_code,
            country=model.country,
            is_primary=model.is_primary
        )
    
    def validate(self) -> list:
        """Validate address data."""
        from app.utils.validators import validate_required
        
        errors = []
        
        is_valid, error = validate_required(self.street, "Street")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_required(self.city, "City")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_required(self.zip_code, "ZIP code")
        if not is_valid:
            errors.append(error)
        
        if self.address_type not in ('billing', 'shipping'):
            errors.append("Address type must be 'billing' or 'shipping'")
        
        return errors


@dataclass
class CustomerSchema(BaseSchema):
    """Schema for customer responses."""
    
    id: UUID
    user_id: UUID
    email: str
    first_name: str
    last_name: str
    company_name: Optional[str]
    phone: Optional[str]
    credit_terms: str
    is_active: bool
    created_at: datetime
    addresses: List[AddressSchema] = field(default_factory=list)
    
    @property
    def display_name(self) -> str:
        if self.company_name:
            return self.company_name
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def from_model(cls, model, include_addresses: bool = False) -> 'CustomerSchema':
        addresses = []
        if include_addresses and hasattr(model, 'addresses'):
            addresses = [AddressSchema.from_model(a) for a in model.addresses]
        
        return cls(
            id=model.id,
            user_id=model.user_id,
            email=model.user.email if model.user else None,
            first_name=model.user.first_name if model.user else '',
            last_name=model.user.last_name if model.user else '',
            company_name=model.company_name,
            phone=model.phone,
            credit_terms=model.credit_terms,
            is_active=model.is_active,
            created_at=model.created_at,
            addresses=addresses
        )


@dataclass
class CustomerCreateSchema(BaseSchema):
    """Schema for customer registration."""
    
    email: str
    password: str
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    phone: Optional[str] = None
    credit_terms: str = 'Net 30'
    
    def validate(self) -> list:
        """Validate customer registration data."""
        from app.utils.validators import (
            validate_email, validate_password, validate_name, validate_phone
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
        
        if self.phone:
            is_valid, error = validate_phone(self.phone)
            if not is_valid:
                errors.append(f"Phone: {error}")
        
        return errors


@dataclass
class CustomerUpdateSchema(BaseSchema):
    """Schema for customer profile updates."""
    
    company_name: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    credit_terms: Optional[str] = None
    
    def validate(self) -> list:
        """Validate update data."""
        from app.utils.validators import validate_phone
        
        errors = []
        
        if self.phone:
            is_valid, error = validate_phone(self.phone)
            if not is_valid:
                errors.append(f"Phone: {error}")
        
        return errors
