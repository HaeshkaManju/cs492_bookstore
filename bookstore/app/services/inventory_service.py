"""
Inventory Service
=================

Business logic for inventory management.
Handles stock tracking, adjustments, and low-stock alerts.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from app.models import Inventory, Warehouse, Book
from app.repositories import InventoryRepository, WarehouseRepository, BookRepository
from app.services.base import BaseService, ValidationError, NotFoundError, ConflictError
from app.utils.validators import validate_inventory_data, validate_condition, validate_quantity, validate_money
from app.extensions import db


class InventoryService(BaseService[Inventory]):
    """
    Service for inventory management operations.
    """
    
    def __init__(
        self,
        repository: InventoryRepository = None,
        warehouse_repository: WarehouseRepository = None,
        book_repository: BookRepository = None
    ):
        self.repository = repository or InventoryRepository()
        self.warehouse_repository = warehouse_repository or WarehouseRepository()
        self.book_repository = book_repository or BookRepository()
    
    # =========================================================================
    # Inventory Creation
    # =========================================================================
    
    def add_inventory(
        self,
        book_id: UUID,
        warehouse_id: UUID,
        condition: int,
        quantity: int,
        acquisition_cost: Decimal,
        list_price: Decimal,
        reorder_level: int = 1,
        location_code: Optional[str] = None,
        auto_commit: bool = True
    ) -> Inventory:
        """
        Add inventory for a book.
        
        Creates new record or updates existing if same book/warehouse/condition.
        
        Args:
            book_id: Book ID
            warehouse_id: Warehouse ID
            condition: Condition grade (1-5)
            quantity: Number of copies
            acquisition_cost: Cost per item
            list_price: Selling price
            reorder_level: Low-stock threshold
            location_code: Shelf/bin location
            auto_commit: Whether to commit transaction
            
        Returns:
            Inventory instance (created or updated)
        """
        # Validate inputs
        errors = []
        
        is_valid, error = validate_condition(condition)
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_quantity(quantity, "Quantity", min_value=0)
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_money(str(acquisition_cost))
        if not is_valid:
            errors.append(f"Acquisition cost: {error}")
        
        is_valid, error = validate_money(str(list_price))
        if not is_valid:
            errors.append(f"List price: {error}")
        
        self.validate_and_raise(errors)
        
        # Verify book exists
        book = self.book_repository.get_by_id(book_id)
        if not book:
            raise NotFoundError("Book", book_id)
        
        # Verify warehouse exists
        warehouse = self.warehouse_repository.get_by_id(warehouse_id)
        if not warehouse:
            raise NotFoundError("Warehouse", warehouse_id)
        
        # Check for existing inventory record
        existing = self.repository.get_by_book_and_warehouse(
            book_id, warehouse_id, condition
        )
        
        if existing:
            # Update existing record
            existing.quantity += quantity
            if acquisition_cost:
                # Recalculate average cost
                total_cost = (existing.quantity * float(existing.acquisition_cost)) + (quantity * float(acquisition_cost))
                total_qty = existing.quantity + quantity
                existing.acquisition_cost = Decimal(total_cost / total_qty) if total_qty > 0 else acquisition_cost
            existing.list_price = list_price
            if location_code:
                existing.location_code = location_code
            inventory = existing
        else:
            # Create new record
            inventory = Inventory(
                book_id=book_id,
                warehouse_id=warehouse_id,
                condition=condition,
                quantity=quantity,
                acquisition_cost=acquisition_cost,
                list_price=list_price,
                reorder_level=reorder_level,
                location_code=location_code
            )
            db.session.add(inventory)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return inventory
    
    # =========================================================================
    # Inventory Queries
    # =========================================================================
    
    def get_by_book(
        self,
        book_id: UUID,
        in_stock_only: bool = False
    ) -> List[Inventory]:
        """Get all inventory for a book."""
        return self.repository.get_by_book(book_id, in_stock_only)
    
    def get_by_warehouse(
        self,
        warehouse_id: UUID,
        in_stock_only: bool = False
    ) -> List[Inventory]:
        """Get all inventory in a warehouse."""
        return self.repository.get_by_warehouse(warehouse_id, in_stock_only)
    
    def get_low_stock(
        self,
        warehouse_id: Optional[UUID] = None
    ) -> List[Inventory]:
        """Get items at or below reorder level."""
        return self.repository.get_low_stock(warehouse_id)
    
    def get_out_of_stock(
        self,
        warehouse_id: Optional[UUID] = None
    ) -> List[Inventory]:
        """Get out-of-stock items."""
        return self.repository.get_out_of_stock(warehouse_id)
    
    def get_total_value(
        self,
        warehouse_id: Optional[UUID] = None
    ) -> Dict[str, Decimal]:
        """Get total inventory value."""
        return self.repository.get_total_value(warehouse_id)
    
    def search(
        self,
        query: str,
        warehouse_id: Optional[UUID] = None,
        min_condition: Optional[int] = None,
        in_stock_only: bool = True,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Search inventory by book title/author."""
        return self.repository.search(
            query_str=query,
            warehouse_id=warehouse_id,
            min_condition=min_condition,
            in_stock_only=in_stock_only,
            page=page,
            per_page=per_page
        )
    
    # =========================================================================
    # Quantity Adjustments
    # =========================================================================
    
    def adjust_quantity(
        self,
        inventory_id: UUID,
        delta: int,
        reason: Optional[str] = None,
        auto_commit: bool = True
    ) -> Inventory:
        """
        Adjust inventory quantity.
        
        Args:
            inventory_id: Inventory ID
            delta: Amount to add (positive) or remove (negative)
            reason: Optional adjustment reason (for audit)
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated Inventory instance
        """
        inventory = self.get_or_404(inventory_id, "Inventory")
        
        try:
            inventory.adjust_quantity(delta)
        except ValueError as e:
            raise ValidationError([str(e)])
        
        if auto_commit:
            self.commit()
        
        return inventory
    
    def reserve_inventory(
        self,
        inventory_id: UUID,
        quantity: int,
        auto_commit: bool = True
    ) -> Inventory:
        """
        Reserve inventory for a sale.
        
        Args:
            inventory_id: Inventory ID
            quantity: Quantity to reserve
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated Inventory instance
        """
        inventory = self.get_or_404(inventory_id, "Inventory")
        
        if quantity > inventory.quantity:
            raise ValidationError([
                f"Insufficient inventory: have {inventory.quantity}, need {quantity}"
            ])
        
        inventory.quantity -= quantity
        
        if auto_commit:
            self.commit()
        
        return inventory
    
    def restock(
        self,
        inventory_id: UUID,
        quantity: int,
        unit_cost: Optional[Decimal] = None,
        auto_commit: bool = True
    ) -> Inventory:
        """
        Add stock from purchase order receipt.
        
        Args:
            inventory_id: Inventory ID
            quantity: Quantity to add
            unit_cost: Optional new unit cost
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated Inventory instance
        """
        inventory = self.get_or_404(inventory_id, "Inventory")
        inventory.restock(quantity, unit_cost)
        
        if auto_commit:
            self.commit()
        
        return inventory
    
    # =========================================================================
    # Inventory Updates
    # =========================================================================
    
    def update_pricing(
        self,
        inventory_id: UUID,
        list_price: Optional[Decimal] = None,
        acquisition_cost: Optional[Decimal] = None,
        auto_commit: bool = True
    ) -> Inventory:
        """
        Update inventory pricing.
        
        Args:
            inventory_id: Inventory ID
            list_price: New list price
            acquisition_cost: New acquisition cost
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated Inventory instance
        """
        inventory = self.get_or_404(inventory_id, "Inventory")
        
        errors = []
        
        if list_price is not None:
            is_valid, error = validate_money(str(list_price))
            if not is_valid:
                errors.append(f"List price: {error}")
            else:
                inventory.list_price = list_price
        
        if acquisition_cost is not None:
            is_valid, error = validate_money(str(acquisition_cost))
            if not is_valid:
                errors.append(f"Acquisition cost: {error}")
            else:
                inventory.acquisition_cost = acquisition_cost
        
        self.validate_and_raise(errors)
        
        if auto_commit:
            self.commit()
        
        return inventory
    
    def update_reorder_level(
        self,
        inventory_id: UUID,
        reorder_level: int,
        auto_commit: bool = True
    ) -> Inventory:
        """
        Update reorder level.
        
        Args:
            inventory_id: Inventory ID
            reorder_level: New reorder level
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated Inventory instance
        """
        is_valid, error = validate_quantity(reorder_level, "Reorder level", min_value=0)
        if not is_valid:
            raise ValidationError([error])
        
        inventory = self.get_or_404(inventory_id, "Inventory")
        inventory.reorder_level = reorder_level
        
        if auto_commit:
            self.commit()
        
        return inventory
    
    def update_location(
        self,
        inventory_id: UUID,
        location_code: str,
        auto_commit: bool = True
    ) -> Inventory:
        """
        Update location code.
        
        Args:
            inventory_id: Inventory ID
            location_code: New location code
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated Inventory instance
        """
        inventory = self.get_or_404(inventory_id, "Inventory")
        inventory.location_code = location_code.strip() if location_code else None
        
        if auto_commit:
            self.commit()
        
        return inventory
    
    # =========================================================================
    # Warehouse Management
    # =========================================================================
    
    def get_warehouses(self) -> List[Warehouse]:
        """Get all active warehouses."""
        return self.warehouse_repository.get_active()
    
    def create_warehouse(
        self,
        name: str,
        location: Optional[str] = None,
        capacity: int = 10000,
        auto_commit: bool = True
    ) -> Warehouse:
        """
        Create a new warehouse.
        
        Args:
            name: Warehouse name
            location: Address/location
            capacity: Item capacity
            auto_commit: Whether to commit transaction
            
        Returns:
            Created Warehouse instance
        """
        if not name or not name.strip():
            raise ValidationError(["Warehouse name is required"])
        
        warehouse = Warehouse(
            name=name.strip(),
            location=location.strip() if location else None,
            capacity=capacity
        )
        
        db.session.add(warehouse)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return warehouse
    
    def get_warehouse_stats(self) -> List[Dict[str, Any]]:
        """Get warehouses with inventory statistics."""
        return self.warehouse_repository.get_with_inventory_stats()
