"""
Data Transfer Objects (DTOs) / Schemas
======================================

This module provides data transfer objects for API communication
between modules and external clients.

Design Pattern: Data Transfer Object (DTO)
- Decouples internal models from API contracts
- Provides serialization/deserialization
- Enables API versioning
- Validates input data structure

Usage:
    from app.schemas import BookSchema, InventorySchema
    
    # Serialize model to dict
    book_data = BookSchema.from_model(book).to_dict()
    
    # Create model from request data
    schema = BookSchema.from_dict(request.json)
    book = schema.to_model()

Integration Points:
- API routes use schemas for request/response
- Services can return schemas instead of models
- Enables clean API versioning
"""

from app.schemas.base import BaseSchema
from app.schemas.user import UserSchema, UserCreateSchema, UserUpdateSchema
from app.schemas.customer import CustomerSchema, CustomerCreateSchema, AddressSchema
from app.schemas.book import BookSchema, BookCreateSchema, BookUpdateSchema
from app.schemas.inventory import InventorySchema, InventoryCreateSchema, WarehouseSchema
from app.schemas.invoice import InvoiceSchema, InvoiceCreateSchema, InvoiceLineSchema
from app.schemas.book_request import BookRequestSchema, BookRequestCreateSchema
from app.schemas.purchase_order import PurchaseOrderSchema, POLineSchema, ManufacturerSchema

__all__ = [
    'BaseSchema',
    'UserSchema', 'UserCreateSchema', 'UserUpdateSchema',
    'CustomerSchema', 'CustomerCreateSchema', 'AddressSchema',
    'BookSchema', 'BookCreateSchema', 'BookUpdateSchema',
    'InventorySchema', 'InventoryCreateSchema', 'WarehouseSchema',
    'InvoiceSchema', 'InvoiceCreateSchema', 'InvoiceLineSchema',
    'BookRequestSchema', 'BookRequestCreateSchema',
    'PurchaseOrderSchema', 'POLineSchema', 'ManufacturerSchema',
]
