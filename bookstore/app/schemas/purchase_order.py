"""
Purchase Order Schemas
======================

DTOs for purchase order API operations.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.schemas.base import BaseSchema
from app.models.inventory import CONDITION_LABELS


@dataclass
class ManufacturerSchema(BaseSchema):
    """Schema for manufacturer data."""
    
    id: Optional[UUID] = None
    name: str = ''
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_model(cls, model) -> 'ManufacturerSchema':
        return cls(
            id=model.id,
            name=model.name,
            contact_name=model.contact_name,
            email=model.email,
            phone=model.phone,
            address=model.address,
            is_active=model.is_active,
            created_at=model.created_at
        )
    
    def validate(self) -> list:
        """Validate manufacturer data."""
        from app.utils.validators import validate_required
        
        errors = []
        
        is_valid, error = validate_required(self.name, "Name")
        if not is_valid:
            errors.append(error)
        
        return errors


@dataclass
class POLineSchema(BaseSchema):
    """Schema for PO line item."""
    
    id: Optional[UUID] = None
    po_id: Optional[UUID] = None
    book_id: Optional[UUID] = None
    description: str = ''
    isbn: Optional[str] = None
    expected_condition: Optional[int] = None
    expected_condition_label: Optional[str] = None
    quantity: int = 1
    unit_cost: float = 0.0
    received_qty: int = 0
    line_total: Optional[float] = None
    pending_qty: Optional[int] = None
    is_fully_received: Optional[bool] = None
    
    @classmethod
    def from_model(cls, model) -> 'POLineSchema':
        return cls(
            id=model.id,
            po_id=model.po_id,
            book_id=model.book_id,
            description=model.description,
            isbn=model.isbn,
            expected_condition=model.expected_condition,
            expected_condition_label=CONDITION_LABELS.get(model.expected_condition) if model.expected_condition else None,
            quantity=model.quantity,
            unit_cost=float(model.unit_cost),
            received_qty=model.received_qty,
            line_total=float(model.line_total),
            pending_qty=model.pending_qty,
            is_fully_received=model.is_fully_received
        )


@dataclass
class PurchaseOrderSchema(BaseSchema):
    """Schema for purchase order responses."""
    
    id: UUID
    po_number: str
    manufacturer_id: UUID
    status: str
    total: float
    notes: Optional[str]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    received_at: Optional[datetime]
    # Optional joined data
    manufacturer_name: Optional[str] = None
    creator_name: Optional[str] = None
    line_count: Optional[int] = None
    total_items_ordered: Optional[int] = None
    total_items_received: Optional[int] = None
    is_fully_received: Optional[bool] = None
    lines: List[POLineSchema] = field(default_factory=list)
    
    @classmethod
    def from_model(cls, model, include_lines: bool = False) -> 'PurchaseOrderSchema':
        lines = []
        if include_lines:
            lines = [POLineSchema.from_model(l) for l in model.lines]
        
        manufacturer_name = None
        if model.manufacturer:
            manufacturer_name = model.manufacturer.name
        
        creator_name = None
        if model.creator:
            creator_name = model.creator.full_name
        
        return cls(
            id=model.id,
            po_number=model.po_number,
            manufacturer_id=model.manufacturer_id,
            status=model.status,
            total=float(model.total),
            notes=model.notes,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
            submitted_at=model.submitted_at,
            received_at=model.received_at,
            manufacturer_name=manufacturer_name,
            creator_name=creator_name,
            line_count=model.line_count,
            total_items_ordered=model.total_items_ordered,
            total_items_received=model.total_items_received,
            is_fully_received=model.is_fully_received,
            lines=lines
        )


@dataclass
class PurchaseOrderCreateSchema(BaseSchema):
    """Schema for PO creation."""
    
    manufacturer_id: str  # UUID as string
    notes: Optional[str] = None
    
    def validate(self) -> list:
        """Validate PO creation data."""
        from app.utils.validators import validate_uuid
        
        errors = []
        
        is_valid, error = validate_uuid(self.manufacturer_id, "Manufacturer ID")
        if not is_valid:
            errors.append(error)
        
        return errors


@dataclass
class POLineCreateSchema(BaseSchema):
    """Schema for adding line to PO."""
    
    description: str
    quantity: int
    unit_cost: float
    book_id: Optional[str] = None
    isbn: Optional[str] = None
    expected_condition: Optional[int] = None
    
    def validate(self) -> list:
        """Validate line data."""
        from app.utils.validators import (
            validate_required, validate_quantity, validate_money, validate_condition
        )
        
        errors = []
        
        is_valid, error = validate_required(self.description, "Description")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_quantity(self.quantity, "Quantity")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_money(str(self.unit_cost))
        if not is_valid:
            errors.append(f"Unit cost: {error}")
        
        if self.expected_condition is not None:
            is_valid, error = validate_condition(self.expected_condition)
            if not is_valid:
                errors.append(f"Expected condition: {error}")
        
        return errors


@dataclass
class POReceiveLineSchema(BaseSchema):
    """Schema for receiving PO line items."""
    
    received_qty: int
    
    def validate(self) -> list:
        """Validate receive data."""
        from app.utils.validators import validate_quantity
        
        errors = []
        
        is_valid, error = validate_quantity(self.received_qty, "Received quantity", min_value=0)
        if not is_valid:
            errors.append(error)
        
        return errors
