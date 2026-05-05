# Inventory Management Module

**Related Stories:** US-005  
**Related Tasks:** S2-6 to S2-11

---

## 1. Overview

The Inventory Management Module enables staff to:
- Search and browse book inventory
- View detailed book information with pricing
- Monitor stock levels across warehouses
- Track incoming quantities from pending purchase orders
- Receive low-stock alerts based on reorder thresholds

---

## 2. Definition of Done Reference

From the project DoD (Section 4.1):
> - User shall locate a dedicated Inventory Management section
> - User shall conduct non-technical searches
> - User shall see standard book info (Title, Author, ISBN, prices)
> - User shall see inventory counts per warehouse
> - User shall see incoming (ordered) quantities

---

## 3. Feature Specifications

### 3.1 Inventory Search (S2-11)

| Feature | Description |
|---------|-------------|
| Search Bar | Single input field for text search |
| Search Fields | title, author, isbn, category |
| Filters | Category dropdown, stock status, warehouse |
| Pagination | 25 items per page, total count displayed |
| Sorting | By title, author, quantity, price |

**Search Algorithm:**
- Full-text search on title, author using PostgreSQL `tsvector`
- Exact match on ISBN
- Case-insensitive, partial match supported

### 3.2 Book Details View (S2-8)

| Field | Source | Display |
|-------|--------|---------|
| Title | BOOK.title | Primary heading |
| Author | BOOK.author | Subtitle |
| ISBN | BOOK.isbn | Formatted ISBN-13 |
| Publisher | BOOK.publisher | Metadata |
| Category | BOOK.category | Badge/tag |
| Manufacturer Price | BOOK.mfr_price | Cost column |
| List Price | BOOK.list_price | Sale price |
| Description | BOOK.description | Expandable |

### 3.3 Inventory Counts (S2-9)

| Display | Data Source |
|---------|-------------|
| Total Stock | SUM(INVENTORY.quantity) for book |
| By Warehouse | INVENTORY joined with WAREHOUSE |
| Reorder Level | INVENTORY.reorder_level |
| Status | Calculated: In Stock / Low / Out of Stock |

**Status Calculation:**
```python
if total_quantity == 0:
    status = "OUT_OF_STOCK"
elif total_quantity <= reorder_level:
    status = "LOW_STOCK"
else:
    status = "IN_STOCK"
```

### 3.4 Incoming Quantities (S2-10)

Shows pending purchase order quantities:
```sql
SELECT SUM(po_line.quantity) as incoming
FROM purchase_order_line po_line
JOIN purchase_order po ON po.id = po_line.po_id
WHERE po_line.book_id = :book_id
  AND po.status IN ('submitted', 'shipped')
```

---

## 4. UI Components

### 4.1 Inventory List Page

```
┌─────────────────────────────────────────────────────────────────┐
│  Inventory Management                              [+ Add Book] │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────┐  Category: [All ▼]        │
│  │ 🔍 Search by title, author, ISBN│  Stock: [All ▼]           │
│  └─────────────────────────────────┘  Warehouse: [All ▼]       │
├─────────────────────────────────────────────────────────────────┤
│  ISBN          │ Title         │ Author    │ Stock │ Status    │
├────────────────┼───────────────┼───────────┼───────┼───────────┤
│  978-0-13-... │ Clean Code    │ R. Martin │   45  │ ● In Stock│
│  978-0-59-... │ JavaScript... │ D. Flana. │    8  │ ● Low     │
│  978-0-32-... │ Design Patt.. │ GoF       │    0  │ ● Out     │
├─────────────────────────────────────────────────────────────────┤
│  Showing 1-25 of 1,234 books              [< Prev] [Next >]    │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Book Detail Modal

```
┌─────────────────────────────────────────────────────────────────┐
│  Clean Code                                              [Edit] │
│  Robert C. Martin                                               │
├─────────────────────────────────────────────────────────────────┤
│  ISBN: 978-0-13-235088-4     Category: Programming              │
│  Publisher: Prentice Hall                                       │
├─────────────────────────────────────────────────────────────────┤
│  PRICING                     │  STOCK LEVELS                    │
│  Manufacturer: $35.00        │  Main Warehouse:     35          │
│  List Price:   $49.99        │  Downtown Store:     10          │
│  Margin:       42.9%         │  ─────────────────────           │
│                              │  Total:              45          │
│                              │  Incoming (PO):      +20         │
│                              │  Reorder Level:      15          │
├─────────────────────────────────────────────────────────────────┤
│  [Create Purchase Order]              [View Sales History]      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. API Endpoints

### 5.1 Inventory Routes

| Method | Endpoint | Description | Task |
|--------|----------|-------------|------|
| GET | /api/inventory | List all inventory with pagination | S2-7 |
| GET | /api/inventory/search | Search inventory | S2-11 |
| GET | /api/inventory/{book_id} | Get book details with stock | S2-8 |
| GET | /api/inventory/{book_id}/warehouses | Stock by warehouse | S2-9 |
| GET | /api/inventory/{book_id}/incoming | Pending PO quantities | S2-10 |
| POST | /api/inventory | Add new book | US-005 |
| PUT | /api/inventory/{book_id} | Update book details | US-005 |
| DELETE | /api/inventory/{book_id} | Soft-delete book | US-005 |
| PUT | /api/inventory/{book_id}/stock | Adjust stock manually | US-005 |

### 5.2 Request/Response Schemas

```python
# backend/app/schemas/inventory.py

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from enum import Enum

class StockStatus(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"

class BookBase(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: Optional[str] = None
    mfr_price: Decimal
    list_price: Decimal
    category: Optional[str] = None
    description: Optional[str] = None

class BookCreate(BookBase):
    initial_quantity: int = 0
    warehouse_id: UUID

class BookResponse(BookBase):
    id: UUID
    total_quantity: int
    incoming_quantity: int
    status: StockStatus
    
class WarehouseStock(BaseModel):
    warehouse_id: UUID
    warehouse_name: str
    quantity: int
    reorder_level: int

class BookDetailResponse(BookResponse):
    warehouse_stocks: List[WarehouseStock]

class InventorySearchParams(BaseModel):
    q: Optional[str] = None  # Search query
    category: Optional[str] = None
    status: Optional[StockStatus] = None
    warehouse_id: Optional[UUID] = None
    page: int = 1
    per_page: int = 25
    sort_by: str = "title"
    sort_order: str = "asc"
```

---

## 6. Service Layer

```python
# backend/app/services/inventory_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import Book, Inventory, PurchaseOrderLine, PurchaseOrder
from app.schemas.inventory import InventorySearchParams, StockStatus

class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search_inventory(self, params: InventorySearchParams):
        query = select(Book).where(Book.is_active == True)
        
        if params.q:
            search_term = f"%{params.q}%"
            query = query.where(
                (Book.title.ilike(search_term)) |
                (Book.author.ilike(search_term)) |
                (Book.isbn.ilike(search_term))
            )
        
        if params.category:
            query = query.where(Book.category == params.category)
        
        # Add pagination
        offset = (params.page - 1) * params.per_page
        query = query.offset(offset).limit(params.per_page)
        
        result = await self.db.execute(query)
        books = result.scalars().all()
        
        # Enrich with stock data
        return [await self._enrich_book(book) for book in books]
    
    async def get_total_stock(self, book_id: UUID) -> int:
        result = await self.db.execute(
            select(func.sum(Inventory.quantity))
            .where(Inventory.book_id == book_id)
        )
        return result.scalar() or 0
    
    async def get_incoming_quantity(self, book_id: UUID) -> int:
        result = await self.db.execute(
            select(func.sum(PurchaseOrderLine.quantity))
            .join(PurchaseOrder)
            .where(PurchaseOrderLine.book_id == book_id)
            .where(PurchaseOrder.status.in_(['submitted', 'shipped']))
        )
        return result.scalar() or 0
```

---

## 7. Low-Stock Alerts

### 7.1 Alert Generation

Books are flagged when `quantity <= reorder_level`:

```python
async def get_low_stock_books(self) -> List[Book]:
    query = """
        SELECT b.*, i.quantity, i.reorder_level
        FROM books b
        JOIN inventory i ON b.id = i.book_id
        WHERE i.quantity <= i.reorder_level
          AND b.is_active = true
        ORDER BY i.quantity ASC
    """
    return await self.db.execute(query)
```

### 7.2 Dashboard Widget

Low-stock alert displayed on Admin Dashboard:
- Count of items below reorder level
- Click to view filtered list
- Option to create bulk PO

---

## 8. Testing Requirements

| Test Case | Description | Type |
|-----------|-------------|------|
| INV-001 | Search returns correct results | Integration |
| INV-002 | Pagination works correctly | Unit |
| INV-003 | Stock counts accurate per warehouse | Integration |
| INV-004 | Incoming quantity calculation correct | Integration |
| INV-005 | Low-stock status calculated correctly | Unit |
| INV-006 | Only admin/employee can access | Security |
| INV-007 | Search performance < 1 second | Performance |

---

## Next Document: [05-SALES-MODULE.md](05-SALES-MODULE.md)
