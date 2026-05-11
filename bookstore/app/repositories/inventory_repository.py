"""
Inventory Repository
====================

Data access for Inventory and Warehouse models.
Handles stock queries, low-stock alerts, and inventory management.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy import func, and_

from app.models import Inventory, Warehouse, Book
from app.repositories.base import BaseRepository
from app.extensions import db


class InventoryRepository(BaseRepository[Inventory]):
    """
    Repository for Inventory data access.
    """
    
    model_class = Inventory
    
    def get_by_book_and_warehouse(
        self,
        book_id: UUID,
        warehouse_id: UUID,
        condition: int
    ) -> Optional[Inventory]:
        """
        Get specific inventory record.
        
        Args:
            book_id: Book ID
            warehouse_id: Warehouse ID
            condition: Condition grade (1-5)
            
        Returns:
            Inventory instance or None
        """
        return Inventory.query.filter_by(
            book_id=book_id,
            warehouse_id=warehouse_id,
            condition=condition
        ).first()
    
    def get_by_book(
        self,
        book_id: UUID,
        in_stock_only: bool = False
    ) -> List[Inventory]:
        """
        Get all inventory for a book.
        
        Args:
            book_id: Book ID
            in_stock_only: Only return items with quantity > 0
            
        Returns:
            List of Inventory instances
        """
        query = Inventory.query.filter_by(book_id=book_id)
        
        if in_stock_only:
            query = query.filter(Inventory.quantity > 0)
        
        return query.order_by(
            Inventory.condition.desc(),
            Inventory.list_price.asc()
        ).all()
    
    def get_by_warehouse(
        self,
        warehouse_id: UUID,
        in_stock_only: bool = False
    ) -> List[Inventory]:
        """
        Get all inventory in a warehouse.
        
        Args:
            warehouse_id: Warehouse ID
            in_stock_only: Only return items with quantity > 0
            
        Returns:
            List of Inventory instances
        """
        query = Inventory.query.filter_by(warehouse_id=warehouse_id)
        
        if in_stock_only:
            query = query.filter(Inventory.quantity > 0)
        
        return query.join(Book).order_by(Book.title).all()
    
    def get_low_stock(
        self,
        warehouse_id: Optional[UUID] = None
    ) -> List[Inventory]:
        """
        Get inventory items at or below reorder level.
        
        Args:
            warehouse_id: Optional warehouse filter
            
        Returns:
            List of low-stock Inventory instances
        """
        query = Inventory.query.filter(
            Inventory.quantity <= Inventory.reorder_level,
            Inventory.quantity > 0
        )
        
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        
        return query.join(Book).order_by(
            Inventory.quantity.asc(),
            Book.title
        ).all()
    
    def get_out_of_stock(
        self,
        warehouse_id: Optional[UUID] = None
    ) -> List[Inventory]:
        """
        Get out-of-stock inventory items.
        
        Args:
            warehouse_id: Optional warehouse filter
            
        Returns:
            List of out-of-stock Inventory instances
        """
        query = Inventory.query.filter(Inventory.quantity == 0)
        
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        
        return query.join(Book).order_by(Book.title).all()
    
    def get_total_value(
        self,
        warehouse_id: Optional[UUID] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate total inventory value.
        
        Args:
            warehouse_id: Optional warehouse filter
            
        Returns:
            Dict with 'acquisition_value' and 'list_value'
        """
        query = Inventory.query
        
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        
        result = query.with_entities(
            func.sum(Inventory.quantity * Inventory.acquisition_cost).label('acquisition'),
            func.sum(Inventory.quantity * Inventory.list_price).label('list')
        ).first()
        
        return {
            'acquisition_value': Decimal(result.acquisition or 0),
            'list_value': Decimal(result.list or 0)
        }
    
    def get_by_condition(
        self,
        condition: int,
        warehouse_id: Optional[UUID] = None
    ) -> List[Inventory]:
        """
        Get inventory items by condition grade.
        
        Args:
            condition: Condition grade (1-5)
            warehouse_id: Optional warehouse filter
            
        Returns:
            List of Inventory instances
        """
        query = Inventory.query.filter(
            Inventory.condition == condition,
            Inventory.quantity > 0
        )
        
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        
        return query.join(Book).order_by(Book.title).all()
    
    def search(
        self,
        query_str: str,
        warehouse_id: Optional[UUID] = None,
        min_condition: Optional[int] = None,
        in_stock_only: bool = True,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search inventory by book title/author.
        
        Args:
            query_str: Search string
            warehouse_id: Optional warehouse filter
            min_condition: Minimum condition filter
            in_stock_only: Only return in-stock items
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        search = f"%{query_str}%"
        
        query = Inventory.query.join(Book).filter(
            (Book.title.ilike(search)) | (Book.author.ilike(search))
        )
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        if min_condition:
            query = query.filter(Inventory.condition >= min_condition)
        
        if in_stock_only:
            query = query.filter(Inventory.quantity > 0)
        
        query = query.order_by(Book.title, Inventory.condition.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    
    def adjust_quantity(
        self,
        inventory_id: UUID,
        delta: int
    ) -> Inventory:
        """
        Adjust inventory quantity.
        
        Args:
            inventory_id: Inventory ID
            delta: Amount to add (positive) or remove (negative)
            
        Returns:
            Updated Inventory instance
            
        Raises:
            ValueError: If adjustment would result in negative quantity
        """
        inventory = self.get_by_id(inventory_id)
        if not inventory:
            raise ValueError(f"Inventory {inventory_id} not found")
        
        inventory.adjust_quantity(delta)
        db.session.flush()
        return inventory


class WarehouseRepository(BaseRepository[Warehouse]):
    """
    Repository for Warehouse data access.
    """
    
    model_class = Warehouse
    
    def get_active(self) -> List[Warehouse]:
        """Get all active warehouses."""
        return Warehouse.query.filter_by(is_active=True).order_by(Warehouse.name).all()
    
    def get_with_inventory_stats(self) -> List[Dict[str, Any]]:
        """
        Get warehouses with inventory statistics.
        
        Returns:
            List of dicts with warehouse data and stats
        """
        warehouses = self.get_active()
        
        results = []
        for wh in warehouses:
            stats = {
                'warehouse': wh,
                'total_items': wh.get_total_items(),
                'utilization': wh.get_utilization(),
                'unique_titles': Inventory.query.filter_by(
                    warehouse_id=wh.id
                ).distinct(Inventory.book_id).count()
            }
            results.append(stats)
        
        return results
