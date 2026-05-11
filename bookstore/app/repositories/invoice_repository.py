"""
Invoice Repository
==================

Data access for Invoice and InvoiceLine models.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, and_

from app.models import Invoice, InvoiceLine, Customer
from app.repositories.base import BaseRepository
from app.extensions import db


class InvoiceRepository(BaseRepository[Invoice]):
    """
    Repository for Invoice data access.
    """
    
    model_class = Invoice
    
    def get_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """
        Get invoice by invoice number.
        
        Args:
            invoice_number: Invoice number string
            
        Returns:
            Invoice instance or None
        """
        return Invoice.query.filter_by(invoice_number=invoice_number).first()
    
    def get_by_customer(
        self,
        customer_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get invoices for a customer.
        
        Args:
            customer_id: Customer ID
            status: Optional status filter
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        query = Invoice.query.filter_by(customer_id=customer_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(Invoice.created_at.desc())
        
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
        Get invoices by status.
        
        Args:
            status: Invoice status
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        query = Invoice.query.filter_by(status=status).order_by(
            Invoice.created_at.desc()
        )
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    
    def get_unpaid(self, days_old: Optional[int] = None) -> List[Invoice]:
        """
        Get unpaid (sent) invoices.
        
        Args:
            days_old: Optional minimum age in days
            
        Returns:
            List of unpaid Invoice instances
        """
        query = Invoice.query.filter_by(status='sent')
        
        if days_old:
            cutoff = datetime.utcnow() - timedelta(days=days_old)
            query = query.filter(Invoice.sent_at < cutoff)
        
        return query.order_by(Invoice.sent_at.asc()).all()
    
    def get_overdue(self, payment_days: int = 30) -> List[Invoice]:
        """
        Get overdue invoices (sent but not paid after payment terms).
        
        Args:
            payment_days: Days until invoice is overdue
            
        Returns:
            List of overdue Invoice instances
        """
        cutoff = datetime.utcnow() - timedelta(days=payment_days)
        
        return Invoice.query.filter(
            Invoice.status == 'sent',
            Invoice.sent_at < cutoff
        ).order_by(Invoice.sent_at.asc()).all()
    
    def get_totals_by_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get invoice counts and totals by status.
        
        Returns:
            Dict mapping status to count and total
        """
        results = db.session.query(
            Invoice.status,
            func.count(Invoice.id).label('count'),
            func.sum(Invoice.subtotal).label('total')
        ).group_by(Invoice.status).all()
        
        return {
            r.status: {
                'count': r.count,
                'total': Decimal(r.total or 0)
            }
            for r in results
        }
    
    def get_revenue_by_period(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """
        Calculate revenue for a period (paid invoices only).
        
        Args:
            start_date: Period start
            end_date: Period end
            
        Returns:
            Total revenue as Decimal
        """
        result = Invoice.query.filter(
            Invoice.status == 'paid',
            Invoice.paid_at >= start_date,
            Invoice.paid_at <= end_date
        ).with_entities(func.sum(Invoice.subtotal)).scalar()
        
        return Decimal(result or 0)
    
    def get_with_lines(self, invoice_id: UUID) -> Optional[Invoice]:
        """
        Get invoice with line items eagerly loaded.
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            Invoice instance with lines
        """
        return Invoice.query.options(
            db.joinedload(Invoice.lines)
        ).get(invoice_id)
    
    def search(
        self,
        query_str: str,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search invoices by number or customer name.
        
        Args:
            query_str: Search string
            status: Optional status filter
            page: Page number
            per_page: Items per page
            
        Returns:
            Paginated results dict
        """
        from app.models import User
        
        search = f"%{query_str}%"
        
        query = Invoice.query.join(Customer).join(User).filter(
            (Invoice.invoice_number.ilike(search)) |
            (User.first_name.ilike(search)) |
            (User.last_name.ilike(search)) |
            (Customer.company_name.ilike(search))
        )
        
        if status:
            query = query.filter(Invoice.status == status)
        
        query = query.order_by(Invoice.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }


class InvoiceLineRepository(BaseRepository[InvoiceLine]):
    """
    Repository for InvoiceLine data access.
    """
    
    model_class = InvoiceLine
    
    def get_by_invoice(self, invoice_id: UUID) -> List[InvoiceLine]:
        """
        Get all lines for an invoice.
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            List of InvoiceLine instances
        """
        return InvoiceLine.query.filter_by(
            invoice_id=invoice_id
        ).order_by(InvoiceLine.created_at).all()
    
    def get_pending_lines(self, invoice_id: UUID) -> List[InvoiceLine]:
        """
        Get pending (request) lines for an invoice.
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            List of pending InvoiceLine instances
        """
        return InvoiceLine.query.filter_by(
            invoice_id=invoice_id,
            is_pending=True
        ).all()
