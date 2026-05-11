"""
Purchase Order Repository
=========================

Data access for PurchaseOrder, POLine, and Manufacturer models.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import func

from app.models import PurchaseOrder, POLine, Manufacturer
from app.repositories.base import BaseRepository
from app.extensions import db


class ManufacturerRepository(BaseRepository[Manufacturer]):
    """
    Repository for Manufacturer data access.
    """
    
    model_class = Manufacturer
    
    def get_active(self) -> List[Manufacturer]:
        """Get all active manufacturers."""
        return Manufacturer.query.filter_by(
            is_active=True
        ).order_by(Manufacturer.name).all()
    
    def search(self, query_str: str) -> List[Manufacturer]:
        """
        Search manufacturers by name.
        
        Args:
            query_str: Search string
            
        Returns:
            List of matching Manufacturer instances
        """
        search = f"%{query_str}%"
        return Manufacturer.query.filter(
            Manufacturer.name.ilike(search),
            Manufacturer.is_active == True
        ).order_by(Manufacturer.name).all()
    
    def get_with_orders(self, manufacturer_id: UUID) -> Optional[Manufacturer]:
        """
        Get manufacturer with orders eagerly loaded.
        
        Args:
            manufacturer_id: Manufacturer ID
            
        Returns:
            Manufacturer instance with orders
        """
        return Manufacturer.query.options(
            db.joinedload(Manufacturer.purchase_orders)
        ).get(manufacturer_id)


class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):
    """
    Repository for PurchaseOrder data access.
    """
    
    model_class = PurchaseOrder
    
    def get_by_number(self, po_number: str) -> Optional[PurchaseOrder]:
        """
        Get PO by PO number.
        
        Args:
            po_number: PO number string
            
        Returns:
            PurchaseOrder instance or None
        """
        return PurchaseOrder.query.filter_by(po_number=po_number).first()
    
    def get_by_manufacturer(
        self,
        manufacturer_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get POs for a manufacturer.
        
        Args:
            manufacturer_id: Manufacturer ID
            status: Optional status filter
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        query = PurchaseOrder.query.filter_by(manufacturer_id=manufacturer_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(PurchaseOrder.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    
    def get_by_status(
        self,
        status: str,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get POs by status.
        
        Args:
            status: PO status
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        query = PurchaseOrder.query.filter_by(
            status=status
        ).order_by(PurchaseOrder.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    
    def get_awaiting_receipt(self) -> List[PurchaseOrder]:
        """
        Get POs awaiting receipt (submitted, confirmed, or shipped).
        
        Returns:
            List of PurchaseOrder instances
        """
        return PurchaseOrder.query.filter(
            PurchaseOrder.status.in_(['submitted', 'confirmed', 'shipped'])
        ).order_by(PurchaseOrder.submitted_at.asc()).all()
    
    def get_drafts(self, created_by: Optional[UUID] = None) -> List[PurchaseOrder]:
        """
        Get draft POs.
        
        Args:
            created_by: Optional user filter
            
        Returns:
            List of draft PurchaseOrder instances
        """
        query = PurchaseOrder.query.filter_by(status='draft')
        
        if created_by:
            query = query.filter_by(created_by=created_by)
        
        return query.order_by(PurchaseOrder.created_at.desc()).all()
    
    def get_totals_by_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get PO counts and totals by status.
        
        Returns:
            Dict mapping status to count and total
        """
        results = db.session.query(
            PurchaseOrder.status,
            func.count(PurchaseOrder.id).label('count'),
            func.sum(PurchaseOrder.total).label('total')
        ).group_by(PurchaseOrder.status).all()
        
        return {
            r.status: {
                'count': r.count,
                'total': Decimal(r.total or 0)
            }
            for r in results
        }
    
    def get_spending_by_period(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """
        Calculate spending for a period (received POs only).
        
        Args:
            start_date: Period start
            end_date: Period end
            
        Returns:
            Total spending as Decimal
        """
        result = PurchaseOrder.query.filter(
            PurchaseOrder.status == 'received',
            PurchaseOrder.received_at >= start_date,
            PurchaseOrder.received_at <= end_date
        ).with_entities(func.sum(PurchaseOrder.total)).scalar()
        
        return Decimal(result or 0)
    
    def get_with_lines(self, po_id: UUID) -> Optional[PurchaseOrder]:
        """
        Get PO with line items eagerly loaded.
        
        Args:
            po_id: PurchaseOrder ID
            
        Returns:
            PurchaseOrder instance with lines
        """
        return PurchaseOrder.query.options(
            db.joinedload(PurchaseOrder.lines)
        ).get(po_id)
    
    def search(
        self,
        query_str: str,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search POs by number or manufacturer name.
        
        Args:
            query_str: Search string
            status: Optional status filter
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        search = f"%{query_str}%"
        
        query = PurchaseOrder.query.join(Manufacturer).filter(
            (PurchaseOrder.po_number.ilike(search)) |
            (Manufacturer.name.ilike(search))
        )
        
        if status:
            query = query.filter(PurchaseOrder.status == status)
        
        query = query.order_by(PurchaseOrder.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }


class POLineRepository(BaseRepository[POLine]):
    """
    Repository for POLine data access.
    """
    
    model_class = POLine
    
    def get_by_po(self, po_id: UUID) -> List[POLine]:
        """
        Get all lines for a PO.
        
        Args:
            po_id: PurchaseOrder ID
            
        Returns:
            List of POLine instances
        """
        return POLine.query.filter_by(
            po_id=po_id
        ).order_by(POLine.created_at).all()
    
    def get_unreceived(self, po_id: UUID) -> List[POLine]:
        """
        Get lines with unreceived quantity.
        
        Args:
            po_id: PurchaseOrder ID
            
        Returns:
            List of POLine instances with pending quantity
        """
        return POLine.query.filter(
            POLine.po_id == po_id,
            POLine.received_qty < POLine.quantity
        ).all()
