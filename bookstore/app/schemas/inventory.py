"""
Inventory Schemas
=================

DTOs for inventory API operations.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from app.schemas.base import BaseSchema
from app.models.inventory import CONDITION_LABELS


@dataclass
class WarehouseSchema(BaseSchema):
    """Schema for warehouse data."""
    
    id: UUID
    name: str
    location: Optional[str]
    capacity: int
    is_active: bool
    created_at: datetime
    # Optional computed fields
    total_items: Optional[int] = None
    utilization: Optional[float] = None
    
    @classmethod
    def from_model(cls, model, include_stats: bool = False) -> 'WarehouseSchema':
        total_items = None
        utilization = None
        
        if include_stats:
            total_items = model.get_total_items()
            utilization = model.get_utilization()
        
        return cls(
            id=model.id,
            name=model.name,
            location=model.location,
            capacity=model.capacity,
            is_active=model.is_active,
            created_at=model.created_at,
            total_items=total_items,
            utilization=utilization
        )


@dataclass
class InventorySchema(BaseSchema):
    """Schema for inventory responses."""
    
    id: UUID
    book_id: UUID
    warehouse_id: UUID
    condition: int
    condition_label: str
    quantity: int
    acquisition_cost: float
    list_price: float
    reorder_level: int
    location_code: Optional[str]
    created_at: datetime
    updated_at: datetime
    # Optional joined data
    book_title: Optional[str] = None
    book_author: Optional[str] = None
    warehouse_name: Optional[str] = None
    is_low_stock: Optional[bool] = None
    
    @classmethod
    def from_model(cls, model, include_related: bool = True) -> 'InventorySchema':
        book_title = None
        book_author = None
        warehouse_name = None
        
        if include_related:
            if model.book:
                book_title = model.book.title
                book_author = model.book.author
            if model.warehouse:
                warehouse_name = model.warehouse.name
        
        return cls(
            id=model.id,
            book_id=model.book_id,
            warehouse_id=model.warehouse_id,
            condition=model.condition,
            condition_label=CONDITION_LABELS.get(model.condition, 'Unknown'),
            quantity=model.quantity,
            acquisition_cost=float(model.acquisition_cost),
            list_price=float(model.list_price),
            reorder_level=model.reorder_level,
            location_code=model.location_code,
            created_at=model.created_at,
            updated_at=model.updated_at,
            book_title=book_title,
            book_author=book_author,
            warehouse_name=warehouse_name,
            is_low_stock=model.is_low_stock
        )


@dataclass
class InventoryCreateSchema(BaseSchema):
    """Schema for adding inventory."""
    
    book_id: str  # UUID as string from API
    warehouse_id: str
    condition: int
    quantity: int
    acquisition_cost: float
    list_price: float
    reorder_level: int = 1
    location_code: Optional[str] = None
    
    def validate(self) -> list:
        """Validate inventory data."""
        from app.utils.validators import (
            validate_uuid, validate_condition, validate_quantity, validate_money
        )
        
        errors = []
        
        is_valid, error = validate_uuid(self.book_id, "Book ID")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_uuid(self.warehouse_id, "Warehouse ID")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_condition(self.condition)
        if not is_valid:
            errors.append(f"Condition: {error}")
        
        is_valid, error = validate_quantity(self.quantity, "Quantity", min_value=0)
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_money(str(self.acquisition_cost))
        if not is_valid:
            errors.append(f"Acquisition cost: {error}")
        
        is_valid, error = validate_money(str(self.list_price))
        if not is_valid:
            errors.append(f"List price: {error}")
        
        return errors


@dataclass
class InventoryAdjustSchema(BaseSchema):
    """Schema for inventory adjustment."""
    
    delta: int
    reason: Optional[str] = None
    
    def validate(self) -> list:
        """Validate adjustment."""
        errors = []
        if self.delta == 0:
            errors.append("Adjustment delta cannot be zero")
        return errors


@dataclass
class InventorySearchSchema(BaseSchema):
    """Schema for inventory search parameters."""
    
    query: str = ''
    warehouse_id: Optional[str] = None
    min_condition: Optional[int] = None
    in_stock_only: bool = True
    page: int = 1
    per_page: int = 20
