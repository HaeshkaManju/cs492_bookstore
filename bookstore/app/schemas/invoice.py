"""
Invoice Schemas
===============

DTOs for invoice API operations.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from app.schemas.base import BaseSchema
from app.models.inventory import CONDITION_LABELS


@dataclass
class InvoiceLineSchema(BaseSchema):
    """Schema for invoice line item."""
    
    id: Optional[UUID] = None
    invoice_id: Optional[UUID] = None
    line_type: str = 'item'
    book_id: Optional[UUID] = None
    inventory_id: Optional[UUID] = None
    request_id: Optional[UUID] = None
    description: str = ''
    condition: Optional[int] = None
    condition_label: Optional[str] = None
    quantity: int = 1
    unit_price: Optional[float] = None
    line_total: Optional[float] = None
    is_pending: bool = False
    
    @classmethod
    def from_model(cls, model) -> 'InvoiceLineSchema':
        return cls(
            id=model.id,
            invoice_id=model.invoice_id,
            line_type=model.line_type,
            book_id=model.book_id,
            inventory_id=model.inventory_id,
            request_id=model.request_id,
            description=model.description,
            condition=model.condition,
            condition_label=CONDITION_LABELS.get(model.condition) if model.condition else None,
            quantity=model.quantity,
            unit_price=float(model.unit_price) if model.unit_price else None,
            line_total=float(model.line_total) if model.line_total else None,
            is_pending=model.is_pending
        )


@dataclass
class InvoiceSchema(BaseSchema):
    """Schema for invoice responses."""
    
    id: UUID
    invoice_number: str
    customer_id: UUID
    status: str
    subtotal: float
    notes: Optional[str]
    payment_terms: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime]
    paid_at: Optional[datetime]
    # Optional joined data
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    creator_name: Optional[str] = None
    line_count: Optional[int] = None
    has_pending_items: Optional[bool] = None
    lines: List[InvoiceLineSchema] = field(default_factory=list)
    
    @classmethod
    def from_model(cls, model, include_lines: bool = False) -> 'InvoiceSchema':
        lines = []
        if include_lines:
            lines = [InvoiceLineSchema.from_model(l) for l in model.lines]
        
        customer_name = None
        customer_email = None
        if model.customer:
            customer_name = model.customer.display_name
            customer_email = model.customer.email
        
        creator_name = None
        if model.creator:
            creator_name = model.creator.full_name
        
        return cls(
            id=model.id,
            invoice_number=model.invoice_number,
            customer_id=model.customer_id,
            status=model.status,
            subtotal=float(model.subtotal),
            notes=model.notes,
            payment_terms=model.payment_terms,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
            sent_at=model.sent_at,
            paid_at=model.paid_at,
            customer_name=customer_name,
            customer_email=customer_email,
            creator_name=creator_name,
            line_count=model.line_count,
            has_pending_items=model.has_pending_items,
            lines=lines
        )


@dataclass
class InvoiceCreateSchema(BaseSchema):
    """Schema for invoice creation."""
    
    customer_id: str  # UUID as string
    payment_terms: str = 'Net 30'
    notes: Optional[str] = None
    
    def validate(self) -> list:
        """Validate invoice creation data."""
        from app.utils.validators import validate_uuid
        
        errors = []
        
        is_valid, error = validate_uuid(self.customer_id, "Customer ID")
        if not is_valid:
            errors.append(error)
        
        return errors


@dataclass
class InvoiceLineCreateSchema(BaseSchema):
    """Schema for adding inventory line to invoice."""
    
    inventory_id: str
    quantity: int = 1
    
    def validate(self) -> list:
        """Validate line item data."""
        from app.utils.validators import validate_uuid, validate_quantity
        
        errors = []
        
        is_valid, error = validate_uuid(self.inventory_id, "Inventory ID")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_quantity(self.quantity, "Quantity")
        if not is_valid:
            errors.append(error)
        
        return errors


@dataclass 
class InvoiceCustomLineSchema(BaseSchema):
    """Schema for adding custom line to invoice."""
    
    description: str
    quantity: int
    unit_price: float
    
    def validate(self) -> list:
        """Validate custom line data."""
        from app.utils.validators import validate_required, validate_quantity, validate_money
        
        errors = []
        
        is_valid, error = validate_required(self.description, "Description")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_quantity(self.quantity, "Quantity")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_money(str(self.unit_price))
        if not is_valid:
            errors.append(f"Unit price: {error}")
        
        return errors
