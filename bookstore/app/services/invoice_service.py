"""
Invoice Service
===============

Business logic for invoice management.
Handles invoice creation, line items, and status workflow.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from app.models import Invoice, InvoiceLine, Customer, Book, Inventory, BookRequest
from app.repositories import InvoiceRepository, InvoiceLineRepository, CustomerRepository, InventoryRepository
from app.services.base import BaseService, ValidationError, NotFoundError, ConflictError
from app.extensions import db


class InvoiceService(BaseService[Invoice]):
    """
    Service for invoice management operations.
    """
    
    def __init__(
        self,
        repository: InvoiceRepository = None,
        line_repository: InvoiceLineRepository = None,
        customer_repository: CustomerRepository = None,
        inventory_repository: InventoryRepository = None
    ):
        self.repository = repository or InvoiceRepository()
        self.line_repository = line_repository or InvoiceLineRepository()
        self.customer_repository = customer_repository or CustomerRepository()
        self.inventory_repository = inventory_repository or InventoryRepository()
    
    # =========================================================================
    # Invoice Creation
    # =========================================================================
    
    def create_invoice(
        self,
        customer_id: UUID,
        created_by: UUID,
        payment_terms: str = 'Net 30',
        notes: Optional[str] = None,
        auto_commit: bool = True
    ) -> Invoice:
        """
        Create a new draft invoice.
        
        Args:
            customer_id: Customer ID
            created_by: User ID who created the invoice
            payment_terms: Payment terms text
            notes: Optional notes
            auto_commit: Whether to commit transaction
            
        Returns:
            Created Invoice instance
        """
        # Verify customer exists
        customer = self.customer_repository.get_by_id(customer_id)
        if not customer:
            raise NotFoundError("Customer", customer_id)
        
        # Generate invoice number
        invoice_number = Invoice.generate_invoice_number()
        
        invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=customer_id,
            created_by=created_by,
            payment_terms=payment_terms,
            notes=notes.strip() if notes else None,
            status='draft'
        )
        
        db.session.add(invoice)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return invoice
    
    # =========================================================================
    # Line Item Management
    # =========================================================================
    
    def add_inventory_line(
        self,
        invoice_id: UUID,
        inventory_id: UUID,
        quantity: int = 1,
        auto_commit: bool = True
    ) -> InvoiceLine:
        """
        Add an inventory item to invoice.
        
        Args:
            invoice_id: Invoice ID
            inventory_id: Inventory ID to add
            quantity: Quantity to add
            auto_commit: Whether to commit transaction
            
        Returns:
            Created InvoiceLine instance
        """
        invoice = self.get_or_404(invoice_id, "Invoice")
        
        if not invoice.can_edit:
            raise ConflictError(
                "Cannot modify invoice after it has been sent",
                {'status': invoice.status}
            )
        
        # Get inventory item
        inventory = self.inventory_repository.get_by_id(inventory_id)
        if not inventory:
            raise NotFoundError("Inventory", inventory_id)
        
        if inventory.quantity < quantity:
            raise ValidationError([
                f"Insufficient inventory: have {inventory.quantity}, need {quantity}"
            ])
        
        # Create line item
        line = InvoiceLine(
            invoice_id=invoice_id,
            line_type='item',
            book_id=inventory.book_id,
            inventory_id=inventory_id,
            description=f"{inventory.book.title} by {inventory.book.author} ({inventory.condition_label})",
            condition=inventory.condition,
            quantity=quantity,
            unit_price=inventory.list_price,
            is_pending=False
        )
        
        db.session.add(line)
        
        # Recalculate invoice subtotal
        invoice.recalculate_subtotal()
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return line
    
    def add_request_line(
        self,
        invoice_id: UUID,
        request_id: UUID,
        auto_commit: bool = True
    ) -> InvoiceLine:
        """
        Add a pending book request to invoice.
        
        Args:
            invoice_id: Invoice ID
            request_id: Book request ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Created InvoiceLine instance
        """
        invoice = self.get_or_404(invoice_id, "Invoice")
        
        if not invoice.can_edit:
            raise ConflictError(
                "Cannot modify invoice after it has been sent",
                {'status': invoice.status}
            )
        
        # Get book request
        from app.repositories import BookRequestRepository
        request_repo = BookRequestRepository()
        request = request_repo.get_by_id(request_id)
        
        if not request:
            raise NotFoundError("BookRequest", request_id)
        
        # Create pending line item
        line = InvoiceLine(
            invoice_id=invoice_id,
            line_type='request',
            request_id=request_id,
            description=f"[PENDING] {request.title} by {request.author} (Min: {request.min_condition_label})",
            condition=request.min_condition,
            quantity=1,
            unit_price=None,  # Price TBD when fulfilled
            is_pending=True
        )
        
        db.session.add(line)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return line
    
    def add_custom_line(
        self,
        invoice_id: UUID,
        description: str,
        quantity: int,
        unit_price: Decimal,
        auto_commit: bool = True
    ) -> InvoiceLine:
        """
        Add a custom line item to invoice.
        
        Args:
            invoice_id: Invoice ID
            description: Line description
            quantity: Quantity
            unit_price: Price per unit
            auto_commit: Whether to commit transaction
            
        Returns:
            Created InvoiceLine instance
        """
        invoice = self.get_or_404(invoice_id, "Invoice")
        
        if not invoice.can_edit:
            raise ConflictError(
                "Cannot modify invoice after it has been sent",
                {'status': invoice.status}
            )
        
        line = InvoiceLine(
            invoice_id=invoice_id,
            line_type='item',
            description=description.strip(),
            quantity=quantity,
            unit_price=unit_price,
            is_pending=False
        )
        
        db.session.add(line)
        invoice.recalculate_subtotal()
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return line
    
    def remove_line(
        self,
        line_id: UUID,
        auto_commit: bool = True
    ) -> bool:
        """
        Remove a line from invoice.
        
        Args:
            line_id: InvoiceLine ID
            auto_commit: Whether to commit transaction
            
        Returns:
            True if removed
        """
        line = self.line_repository.get_by_id(line_id)
        if not line:
            raise NotFoundError("InvoiceLine", line_id)
        
        invoice = line.invoice
        
        if not invoice.can_edit:
            raise ConflictError(
                "Cannot modify invoice after it has been sent",
                {'status': invoice.status}
            )
        
        db.session.delete(line)
        invoice.recalculate_subtotal()
        
        if auto_commit:
            self.commit()
        
        return True
    
    # =========================================================================
    # Status Workflow
    # =========================================================================
    
    def send_invoice(
        self,
        invoice_id: UUID,
        auto_commit: bool = True
    ) -> Invoice:
        """
        Mark invoice as sent.
        
        Args:
            invoice_id: Invoice ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated Invoice instance
        """
        invoice = self.get_or_404(invoice_id, "Invoice")
        
        if not invoice.can_send:
            if invoice.status != 'draft':
                raise ConflictError(
                    f"Cannot send invoice in status: {invoice.status}",
                    {'current_status': invoice.status}
                )
            if invoice.line_count == 0:
                raise ValidationError(["Cannot send empty invoice"])
        
        invoice.send()
        
        if auto_commit:
            self.commit()
        
        return invoice
    
    def mark_paid(
        self,
        invoice_id: UUID,
        auto_commit: bool = True
    ) -> Invoice:
        """
        Mark invoice as paid.
        
        Args:
            invoice_id: Invoice ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated Invoice instance
        """
        invoice = self.get_or_404(invoice_id, "Invoice")
        
        if not invoice.can_mark_paid:
            raise ConflictError(
                f"Cannot mark as paid invoice in status: {invoice.status}",
                {'current_status': invoice.status}
            )
        
        invoice.mark_paid()
        
        if auto_commit:
            self.commit()
        
        return invoice
    
    def cancel_invoice(
        self,
        invoice_id: UUID,
        auto_commit: bool = True
    ) -> Invoice:
        """
        Cancel an invoice.
        
        Args:
            invoice_id: Invoice ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Cancelled Invoice instance
        """
        invoice = self.get_or_404(invoice_id, "Invoice")
        
        if not invoice.can_cancel:
            raise ConflictError(
                f"Cannot cancel invoice in status: {invoice.status}",
                {'current_status': invoice.status}
            )
        
        invoice.cancel()
        
        if auto_commit:
            self.commit()
        
        return invoice
    
    # =========================================================================
    # Queries
    # =========================================================================
    
    def get_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by number."""
        return self.repository.get_by_number(invoice_number)
    
    def get_by_customer(
        self,
        customer_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get invoices for a customer."""
        return self.repository.get_by_customer(customer_id, status, page, per_page)
    
    def get_by_status(
        self,
        status: str,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get invoices by status."""
        return self.repository.get_by_status(status, page, per_page)
    
    def get_unpaid(self, days_old: Optional[int] = None) -> List[Invoice]:
        """Get unpaid invoices."""
        return self.repository.get_unpaid(days_old)
    
    def get_overdue(self, payment_days: int = 30) -> List[Invoice]:
        """Get overdue invoices."""
        return self.repository.get_overdue(payment_days)
    
    def get_totals_by_status(self) -> Dict[str, Dict[str, Any]]:
        """Get invoice counts and totals by status."""
        return self.repository.get_totals_by_status()
    
    def search(
        self,
        query: str,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Search invoices."""
        return self.repository.search(query, status, page, per_page)
    
    def get_with_lines(self, invoice_id: UUID) -> Optional[Invoice]:
        """Get invoice with lines loaded."""
        return self.repository.get_with_lines(invoice_id)
