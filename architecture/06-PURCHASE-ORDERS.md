# Purchase Order Module

**Related Stories:** US-007  
**Related Tasks:** Sprint 3+ (Post-Sprint 2)

---

## 1. Overview

The Purchase Order Module enables staff to:
- Create purchase orders from low-stock alerts or manual initiation
- Select books with suggested reorder quantities
- Review and edit draft orders before submission
- Generate formatted PO documents for manufacturers
- Track order status through receiving
- Automatically update inventory upon receipt

---

## 2. Definition of Done Reference

From the project DoD (Section 4.3):
> - User shall generate new PO from inventory management interface
> - User shall select books for reorder with default quantities
> - User shall review and edit draft orders
> - User shall receive formatted PO document
> - User shall view open and historical POs
> - System shall track order status
> - Updating to "Received" increases inventory

---

## 3. Purchase Order Lifecycle

```
    ┌────────┐
    │ DRAFT  │ ← Created from low-stock or manual
    └────┬───┘
         │ Submit
         ▼
    ┌────────────┐
    │ SUBMITTED  │ ← PO sent to manufacturer
    └─────┬──────┘
          │ Manufacturer ships
          ▼
    ┌────────────┐
    │  SHIPPED   │ ← In transit
    └─────┬──────┘
          │ Receive shipment
          ▼
    ┌────────────┐
    │  RECEIVED  │ ← Inventory updated
    └────────────┘

    ┌────────────┐
    │ CANCELLED  │ ← Can cancel from DRAFT or SUBMITTED
    └────────────┘
```

---

## 4. Feature Specifications

### 4.1 Create Purchase Order

| Source | Trigger | Action |
|--------|---------|--------|
| Low-Stock Alert | Click "Create PO" on alert | Pre-populate with low-stock books |
| Inventory View | Click "Order More" on book | Pre-populate single book |
| PO Module | Click "New Purchase Order" | Empty draft |

**Default Quantity Calculation:**
```python
suggested_qty = max(
    reorder_level * 2,  # Order 2x the reorder level
    min_order_quantity   # Manufacturer minimum
)
```

### 4.2 Draft Editing

| Editable Field | Constraints |
|----------------|-------------|
| Manufacturer | Select from registered manufacturers |
| Books | Add/remove from draft |
| Quantities | Min 1, max based on warehouse capacity |
| Notes | Free text for special instructions |

### 4.3 PO Document Generation

System generates formatted document containing:
- PO Number (auto-generated)
- Bookstore details (name, address, contact)
- Manufacturer details
- Line items (ISBN, Title, Quantity, Unit Cost, Line Total)
- Order total
- Requested delivery date
- Special instructions

### 4.4 Status Tracking

| Status | Description | Who Updates |
|--------|-------------|-------------|
| Draft | Being edited, not sent | Employee/Admin |
| Submitted | Sent to manufacturer | Admin only |
| Shipped | Manufacturer confirmed shipment | Admin |
| Received | Goods arrived, inventory updated | Admin/Employee |
| Cancelled | Order cancelled | Admin |

---

## 5. UI Components

### 5.1 Purchase Order List

```
┌─────────────────────────────────────────────────────────────────┐
│  Purchase Orders                            [+ New PO]          │
├─────────────────────────────────────────────────────────────────┤
│  Status: [All ▼]  Manufacturer: [All ▼]  Date: [____] to [____]│
├─────────────────────────────────────────────────────────────────┤
│  PO #        │ Manufacturer    │ Items │ Total    │ Status     │
├──────────────┼─────────────────┼───────┼──────────┼────────────┤
│  PO-2026-042 │ Pearson         │  12   │ $456.00  │ ● Draft    │
│  PO-2026-041 │ O'Reilly        │   5   │ $175.00  │ ● Shipped  │
│  PO-2026-040 │ Penguin Books   │   8   │ $280.00  │ ✓ Received │
├─────────────────────────────────────────────────────────────────┤
│  [View Drafts]  [View Open Orders]  [View History]              │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 PO Detail / Edit View

```
┌─────────────────────────────────────────────────────────────────┐
│  Purchase Order: PO-2026-042                    Status: DRAFT   │
├─────────────────────────────────────────────────────────────────┤
│  Manufacturer: [Pearson ▼]                                      │
│  Created: May 5, 2026 by Jane Smith                            │
├─────────────────────────────────────────────────────────────────┤
│  LINE ITEMS                                          [+ Add]    │
│  ─────────────────────────────────────────────────────────────  │
│  ISBN              │ Title              │ Qty │ Cost   │ Total  │
│  978-0-13-235088-4 │ Clean Code         │ [20]│ $35.00 │$700.00 │
│  978-0-13-468599-1 │ Clean Architect... │ [15]│ $40.00 │$600.00 │
│                                                        [Remove] │
│  ─────────────────────────────────────────────────────────────  │
│                                          ORDER TOTAL: $1,300.00 │
├─────────────────────────────────────────────────────────────────┤
│  Notes: _______________________________________________________│
│  Requested Delivery: [May 20, 2026]                            │
├─────────────────────────────────────────────────────────────────┤
│  [Delete Draft]        [Save Draft]        [Submit Order]       │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Receive Shipment

```
┌─────────────────────────────────────────────────────────────────┐
│  Receive Shipment: PO-2026-041                                  │
├─────────────────────────────────────────────────────────────────┤
│  Manufacturer: O'Reilly Media                                   │
│  Submitted: May 1, 2026    Expected: May 15, 2026              │
├─────────────────────────────────────────────────────────────────┤
│  ☑ ISBN              │ Title              │ Ordered │ Received │
│  ☑ 978-0-59-651798-1 │ JavaScript Guide   │   10    │ [10]     │
│  ☑ 978-0-59-651700-4 │ Python Cookbook    │    5    │ [ 5]     │
│  ☐ 978-0-59-600000-0 │ Missing Book       │    5    │ [ 0]     │
├─────────────────────────────────────────────────────────────────┤
│  Warehouse: [Main Warehouse ▼]                                  │
│  Notes: One item back-ordered by manufacturer                  │
├─────────────────────────────────────────────────────────────────┤
│  [Cancel]                              [Confirm Receipt]        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/purchase-orders | List all POs | Admin, Employee |
| POST | /api/purchase-orders | Create new PO | Admin, Employee |
| GET | /api/purchase-orders/{id} | Get PO details | Admin, Employee |
| PUT | /api/purchase-orders/{id} | Update draft PO | Admin, Employee |
| DELETE | /api/purchase-orders/{id} | Delete draft PO | Admin |
| POST | /api/purchase-orders/{id}/submit | Submit PO | Admin |
| POST | /api/purchase-orders/{id}/receive | Receive shipment | Admin, Employee |
| POST | /api/purchase-orders/{id}/cancel | Cancel PO | Admin |
| GET | /api/purchase-orders/{id}/document | Generate PDF | Admin, Employee |

---

## 7. Request/Response Schemas

```python
# backend/app/schemas/purchase_order.py

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from enum import Enum

class POStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class POLineItemCreate(BaseModel):
    book_id: UUID
    quantity: int
    unit_cost: Decimal

class POLineItemResponse(BaseModel):
    id: UUID
    book_id: UUID
    book_isbn: str
    book_title: str
    quantity: int
    unit_cost: Decimal
    line_total: Decimal

class PurchaseOrderCreate(BaseModel):
    manufacturer_id: UUID
    line_items: List[POLineItemCreate]
    notes: Optional[str] = None
    requested_delivery: Optional[datetime] = None

class PurchaseOrderResponse(BaseModel):
    id: UUID
    po_number: str
    manufacturer_id: UUID
    manufacturer_name: str
    status: POStatus
    line_items: List[POLineItemResponse]
    total: Decimal
    notes: Optional[str]
    requested_delivery: Optional[datetime]
    created_by: UUID
    created_at: datetime
    submitted_at: Optional[datetime]
    received_at: Optional[datetime]

class ReceiveLineItem(BaseModel):
    line_id: UUID
    received_quantity: int

class ReceiveShipment(BaseModel):
    line_items: List[ReceiveLineItem]
    warehouse_id: UUID
    notes: Optional[str] = None
```

---

## 8. Service Implementation

### 8.1 Create from Low-Stock Alert

```python
class PurchaseOrderService:
    async def create_from_low_stock(
        self, db: AsyncSession, employee_id: UUID
    ) -> PurchaseOrderResponse:
        # Get all low-stock books grouped by manufacturer
        low_stock = await db.execute("""
            SELECT 
                b.id as book_id,
                b.manufacturer_id,
                i.quantity,
                i.reorder_level
            FROM books b
            JOIN inventory i ON b.id = i.book_id
            WHERE i.quantity <= i.reorder_level
        """)
        
        # Group by manufacturer and create draft POs
        by_manufacturer = {}
        for row in low_stock:
            mfr_id = row.manufacturer_id
            if mfr_id not in by_manufacturer:
                by_manufacturer[mfr_id] = []
            by_manufacturer[mfr_id].append({
                "book_id": row.book_id,
                "quantity": max(row.reorder_level * 2 - row.quantity, 10)
            })
        
        # Create draft POs
        created_pos = []
        for mfr_id, items in by_manufacturer.items():
            po = await self.create(db, PurchaseOrderCreate(
                manufacturer_id=mfr_id,
                line_items=items
            ), employee_id)
            created_pos.append(po)
        
        return created_pos
```

### 8.2 Receive Shipment (Atomic)

```python
async def receive_shipment(
    self, db: AsyncSession,
    po_id: UUID,
    receive_data: ReceiveShipment,
    employee_id: UUID
) -> PurchaseOrderResponse:
    async with db.begin():
        # 1. Get PO and validate status
        po = await self.get_by_id(db, po_id)
        if po.status not in [POStatus.SUBMITTED, POStatus.SHIPPED]:
            raise InvalidPOStatusError()
        
        # 2. Update inventory for each received item
        for item in receive_data.line_items:
            if item.received_quantity > 0:
                # Increment inventory
                await db.execute(
                    update(Inventory)
                    .where(Inventory.book_id == item.book_id)
                    .where(Inventory.warehouse_id == receive_data.warehouse_id)
                    .values(quantity=Inventory.quantity + item.received_quantity)
                )
                
                # Update PO line with received quantity
                await db.execute(
                    update(POLineItem)
                    .where(POLineItem.id == item.line_id)
                    .values(received_quantity=item.received_quantity)
                )
        
        # 3. Update PO status
        po.status = POStatus.RECEIVED
        po.received_at = datetime.utcnow()
        po.received_by = employee_id
        po.receive_notes = receive_data.notes
        
        await db.commit()
        return po
```

---

## 9. Document Generation

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

class PODocumentService:
    def generate_pdf(self, po: PurchaseOrderResponse) -> bytes:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, f"PURCHASE ORDER: {po.po_number}")
        
        # From (Bookstore)
        c.setFont("Helvetica", 10)
        c.drawString(50, 720, "From: Rare Bookstore")
        c.drawString(50, 708, "123 Book Street")
        
        # To (Manufacturer)
        c.drawString(350, 720, f"To: {po.manufacturer_name}")
        
        # Line items table
        y = 650
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "ISBN")
        c.drawString(150, y, "Title")
        c.drawString(350, y, "Qty")
        c.drawString(400, y, "Unit Cost")
        c.drawString(480, y, "Total")
        
        y -= 20
        c.setFont("Helvetica", 10)
        for item in po.line_items:
            c.drawString(50, y, item.book_isbn)
            c.drawString(150, y, item.book_title[:30])
            c.drawString(350, y, str(item.quantity))
            c.drawString(400, y, f"${item.unit_cost:.2f}")
            c.drawString(480, y, f"${item.line_total:.2f}")
            y -= 15
        
        # Total
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, y - 20, f"ORDER TOTAL: ${po.total:.2f}")
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
```

---

## 10. Testing Requirements

| Test Case | Description | Type |
|-----------|-------------|------|
| PO-001 | Create draft PO with line items | Integration |
| PO-002 | Submit PO changes status correctly | Unit |
| PO-003 | Receive shipment updates inventory | Integration |
| PO-004 | Partial receive supported | Integration |
| PO-005 | Cannot edit submitted PO | Unit |
| PO-006 | Admin-only submit permission | Security |
| PO-007 | PDF generation complete | Unit |
| PO-008 | Low-stock auto-populate works | Integration |

---

## Next Document: [07-CUSTOMER-PORTAL.md](07-CUSTOMER-PORTAL.md)
