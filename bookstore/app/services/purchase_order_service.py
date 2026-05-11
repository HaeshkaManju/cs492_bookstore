"""
Purchase Order Service
======================

Business logic for purchase orders to manufacturers.
Handles PO creation, submission, and receipt.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from app.models import PurchaseOrder, POLine, Manufacturer, Inventory
from app.repositories import PurchaseOrderRepository, POLineRepository, ManufacturerRepository, InventoryRepository
from app.services.base import BaseService, ValidationError, NotFoundError, ConflictError
from app.utils.validators import validate_quantity, validate_money, validate_required
from app.extensions import db


class PurchaseOrderService(BaseService[PurchaseOrder]):
    """
    Service for purchase order operations.
    """
    
    def __init__(
        self,
        repository: PurchaseOrderRepository = None,
        line_repository: POLineRepository = None,
        manufacturer_repository: ManufacturerRepository = None,
        inventory_repository: InventoryRepository = None
    ):
        self.repository = repository or PurchaseOrderRepository()
        self.line_repository = line_repository or POLineRepository()
        self.manufacturer_repository = manufacturer_repository or ManufacturerRepository()
        self.inventory_repository = inventory_repository or InventoryRepository()
    
    # =========================================================================
    # Manufacturer Management
    # =========================================================================
    
    def create_manufacturer(
        self,
        name: str,
        contact_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        auto_commit: bool = True
    ) -> Manufacturer:
        """
        Create a new manufacturer.
        
        Args:
            name: Manufacturer name
            contact_name: Primary contact
            email: Contact email
            phone: Contact phone
            address: Mailing address
            auto_commit: Whether to commit transaction
            
        Returns:
            Created Manufacturer instance
        """
        is_valid, error = validate_required(name, "Name")
        if not is_valid:
            raise ValidationError([error])
        
        manufacturer = Manufacturer(
            name=name.strip(),
            contact_name=contact_name.strip() if contact_name else None,
            email=email.strip() if email else None,
            phone=phone.strip() if phone else None,
            address=address.strip() if address else None
        )
        
        db.session.add(manufacturer)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return manufacturer
    
    def get_manufacturers(self) -> List[Manufacturer]:
        """Get all active manufacturers."""
        return self.manufacturer_repository.get_active()
    
    def search_manufacturers(self, query: str) -> List[Manufacturer]:
        """Search manufacturers by name."""
        return self.manufacturer_repository.search(query)
    
    # =========================================================================
    # PO Creation
    # =========================================================================
    
    def create_purchase_order(
        self,
        manufacturer_id: UUID,
        created_by: UUID,
        notes: Optional[str] = None,
        auto_commit: bool = True
    ) -> PurchaseOrder:
        """
        Create a new draft purchase order.
        
        Args:
            manufacturer_id: Manufacturer ID
            created_by: User ID who created the PO
            notes: Optional notes
            auto_commit: Whether to commit transaction
            
        Returns:
            Created PurchaseOrder instance
        """
        # Verify manufacturer exists
        manufacturer = self.manufacturer_repository.get_by_id(manufacturer_id)
        if not manufacturer:
            raise NotFoundError("Manufacturer", manufacturer_id)
        
        # Generate PO number
        po_number = PurchaseOrder.generate_po_number()
        
        po = PurchaseOrder(
            po_number=po_number,
            manufacturer_id=manufacturer_id,
            created_by=created_by,
            notes=notes.strip() if notes else None,
            status='draft'
        )
        
        db.session.add(po)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return po
    
    # =========================================================================
    # Line Item Management
    # =========================================================================
    
    def add_line(
        self,
        po_id: UUID,
        description: str,
        quantity: int,
        unit_cost: Decimal,
        book_id: Optional[UUID] = None,
        isbn: Optional[str] = None,
        expected_condition: Optional[int] = None,
        auto_commit: bool = True
    ) -> POLine:
        """
        Add a line item to purchase order.
        
        Args:
            po_id: PurchaseOrder ID
            description: Item description
            quantity: Quantity to order
            unit_cost: Cost per item
            book_id: Optional book reference
            isbn: ISBN for ordering
            expected_condition: Expected condition grade
            auto_commit: Whether to commit transaction
            
        Returns:
            Created POLine instance
        """
        po = self.get_or_404(po_id, "PurchaseOrder")
        
        if not po.can_edit:
            raise ConflictError(
                "Cannot modify PO after it has been submitted",
                {'status': po.status}
            )
        
        # Validate inputs
        errors = []
        
        is_valid, error = validate_required(description, "Description")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_quantity(quantity, "Quantity")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_money(str(unit_cost))
        if not is_valid:
            errors.append(f"Unit cost: {error}")
        
        self.validate_and_raise(errors)
        
        line = POLine(
            po_id=po_id,
            book_id=book_id,
            description=description.strip(),
            isbn=isbn.strip() if isbn else None,
            expected_condition=expected_condition,
            quantity=quantity,
            unit_cost=unit_cost
        )
        
        db.session.add(line)
        po.recalculate_total()
        
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
        Remove a line from PO.
        
        Args:
            line_id: POLine ID
            auto_commit: Whether to commit transaction
            
        Returns:
            True if removed
        """
        line = self.line_repository.get_by_id(line_id)
        if not line:
            raise NotFoundError("POLine", line_id)
        
        po = line.purchase_order
        
        if not po.can_edit:
            raise ConflictError(
                "Cannot modify PO after it has been submitted",
                {'status': po.status}
            )
        
        db.session.delete(line)
        po.recalculate_total()
        
        if auto_commit:
            self.commit()
        
        return True
    
    # =========================================================================
    # Status Workflow
    # =========================================================================
    
    def submit_po(
        self,
        po_id: UUID,
        auto_commit: bool = True
    ) -> PurchaseOrder:
        """
        Submit PO to manufacturer.
        
        Args:
            po_id: PurchaseOrder ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated PurchaseOrder instance
        """
        po = self.get_or_404(po_id, "PurchaseOrder")
        
        if not po.can_submit:
            if po.status != 'draft':
                raise ConflictError(
                    f"Cannot submit PO in status: {po.status}",
                    {'current_status': po.status}
                )
            if po.line_count == 0:
                raise ValidationError(["Cannot submit empty purchase order"])
        
        po.submit()
        
        if auto_commit:
            self.commit()
        
        return po
    
    def confirm_po(
        self,
        po_id: UUID,
        auto_commit: bool = True
    ) -> PurchaseOrder:
        """
        Mark PO as confirmed by manufacturer.
        
        Args:
            po_id: PurchaseOrder ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated PurchaseOrder instance
        """
        po = self.get_or_404(po_id, "PurchaseOrder")
        
        if po.status != 'submitted':
            raise ConflictError(
                f"Cannot confirm PO in status: {po.status}",
                {'current_status': po.status}
            )
        
        po.confirm()
        
        if auto_commit:
            self.commit()
        
        return po
    
    def mark_shipped(
        self,
        po_id: UUID,
        auto_commit: bool = True
    ) -> PurchaseOrder:
        """
        Mark PO as shipped.
        
        Args:
            po_id: PurchaseOrder ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated PurchaseOrder instance
        """
        po = self.get_or_404(po_id, "PurchaseOrder")
        
        if po.status != 'confirmed':
            raise ConflictError(
                f"Cannot mark shipped PO in status: {po.status}",
                {'current_status': po.status}
            )
        
        po.mark_shipped()
        
        if auto_commit:
            self.commit()
        
        return po
    
    def receive_line(
        self,
        line_id: UUID,
        received_qty: int,
        auto_commit: bool = True
    ) -> POLine:
        """
        Record receipt of items for a PO line.
        
        Args:
            line_id: POLine ID
            received_qty: Quantity received
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated POLine instance
        """
        line = self.line_repository.get_by_id(line_id)
        if not line:
            raise NotFoundError("POLine", line_id)
        
        po = line.purchase_order
        
        if not po.can_receive:
            raise ConflictError(
                f"Cannot receive items for PO in status: {po.status}",
                {'current_status': po.status}
            )
        
        is_valid, error = validate_quantity(received_qty, "Received quantity", min_value=0)
        if not is_valid:
            raise ValidationError([error])
        
        line.receive(received_qty)
        
        if auto_commit:
            self.commit()
        
        return line
    
    def receive_po(
        self,
        po_id: UUID,
        auto_commit: bool = True
    ) -> PurchaseOrder:
        """
        Mark entire PO as received.
        
        This should be called after all lines have been received
        or partial receipt is complete.
        
        Args:
            po_id: PurchaseOrder ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated PurchaseOrder instance
        """
        po = self.get_or_404(po_id, "PurchaseOrder")
        
        if not po.can_receive:
            raise ConflictError(
                f"Cannot receive PO in status: {po.status}",
                {'current_status': po.status}
            )
        
        po.receive()
        
        if auto_commit:
            self.commit()
        
        return po
    
    def cancel_po(
        self,
        po_id: UUID,
        auto_commit: bool = True
    ) -> PurchaseOrder:
        """
        Cancel a purchase order.
        
        Args:
            po_id: PurchaseOrder ID
            auto_commit: Whether to commit transaction
            
        Returns:
            Cancelled PurchaseOrder instance
        """
        po = self.get_or_404(po_id, "PurchaseOrder")
        
        if not po.can_cancel:
            raise ConflictError(
                f"Cannot cancel PO in status: {po.status}",
                {'current_status': po.status}
            )
        
        po.cancel()
        
        if auto_commit:
            self.commit()
        
        return po
    
    # =========================================================================
    # Queries
    # =========================================================================
    
    def get_by_number(self, po_number: str) -> Optional[PurchaseOrder]:
        """Get PO by number."""
        return self.repository.get_by_number(po_number)
    
    def get_by_manufacturer(
        self,
        manufacturer_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get POs for a manufacturer."""
        return self.repository.get_by_manufacturer(manufacturer_id, status, page, per_page)
    
    def get_by_status(
        self,
        status: str,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get POs by status."""
        return self.repository.get_by_status(status, page, per_page)
    
    def get_awaiting_receipt(self) -> List[PurchaseOrder]:
        """Get POs awaiting receipt."""
        return self.repository.get_awaiting_receipt()
    
    def get_drafts(self, created_by: Optional[UUID] = None) -> List[PurchaseOrder]:
        """Get draft POs."""
        return self.repository.get_drafts(created_by)
    
    def get_totals_by_status(self) -> Dict[str, Dict[str, Any]]:
        """Get PO counts and totals by status."""
        return self.repository.get_totals_by_status()
    
    def search(
        self,
        query: str,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Search POs."""
        return self.repository.search(query, status, page, per_page)
    
    def get_with_lines(self, po_id: UUID) -> Optional[PurchaseOrder]:
        """Get PO with lines loaded."""
        return self.repository.get_with_lines(po_id)
