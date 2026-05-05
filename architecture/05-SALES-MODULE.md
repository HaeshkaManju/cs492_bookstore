# Sales Records Module

**Related Stories:** US-006  
**Related Tasks:** Sprint 3+ (Post-Sprint 2)

---

## 1. Overview

The Sales Records Module enables staff to:
- Process in-store sales transactions
- Track all sales with full transaction details
- Search and filter sales records
- Generate summary reports (daily, weekly, monthly)
- Automatically update inventory upon sale completion

---

## 2. Definition of Done Reference

From the project DoD (Section 4.2):
> - User shall access a dedicated module for Sales Records
> - User shall retrieve sales data through flexible search/filtering
> - User shall view clear record of each transaction
> - User shall generate summary reports
> - System shall automatically update inventory upon sale

---

## 3. Feature Specifications

### 3.1 Process Sale

| Step | Action | System Response |
|------|--------|-----------------|
| 1 | Scan/search for book | Display book with price |
| 2 | Add to transaction | Update line items list |
| 3 | Adjust quantity if needed | Recalculate totals |
| 4 | Apply discounts (optional) | Recalculate totals |
| 5 | Select payment method | Enable confirmation |
| 6 | Confirm sale | Create record, decrement inventory |

### 3.2 Transaction Details

| Field | Description |
|-------|-------------|
| Transaction ID | System-generated UUID |
| Date/Time | Timestamp of completion |
| Employee | User who processed sale |
| Customer | Optional linked customer account |
| Line Items | Book, quantity, unit price |
| Subtotal | Sum of line items |
| Tax | Calculated based on location |
| Total | Subtotal + Tax |
| Payment Method | Cash, Card, Account |

### 3.3 Search & Filter Capabilities

| Filter | Type | Options |
|--------|------|---------|
| Date Range | Date picker | Start/End dates |
| Customer | Autocomplete | Customer name/ID |
| Employee | Dropdown | Staff list |
| Book | Search | ISBN/Title/Author |
| Payment Method | Checkbox | Cash, Card, Account |
| Amount Range | Min/Max | Decimal inputs |

### 3.4 Reports

| Report | Description | Metrics |
|--------|-------------|---------|
| Daily Summary | Today's sales | Count, Total, Avg transaction |
| Weekly Summary | Current week | By day breakdown |
| Monthly Summary | Selected month | Trends, comparisons |
| Best Sellers | Top selling books | By quantity, by revenue |
| Employee Performance | Sales by employee | Count, Total |

---

## 4. UI Components

### 4.1 Point of Sale Interface

```
┌─────────────────────────────────────────────────────────────────┐
│  Point of Sale                                Employee: J.Smith │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────┐                            │
│  │ 🔍 Scan or search book...       │                            │
│  └─────────────────────────────────┘                            │
├─────────────────────────────────────────────────────────────────┤
│  CURRENT TRANSACTION                                            │
│  ───────────────────────────────────────────────────────────────│
│  ISBN              │ Title              │ Qty │ Price  │ Total  │
│  978-0-13-235088-4 │ Clean Code         │  1  │ $49.99 │ $49.99 │
│  978-0-59-651798-1 │ JavaScript Guide   │  2  │ $39.99 │ $79.98 │
│  ───────────────────────────────────────────────────────────────│
│                                          Subtotal:     $129.97  │
│  Customer: [Select or Walk-in]           Tax (8.25%):   $10.72  │
│                                          ─────────────────────  │
│                                          TOTAL:        $140.69  │
├─────────────────────────────────────────────────────────────────┤
│  Payment: ( ) Cash  (●) Card  ( ) Account                       │
│                                                                 │
│  [Cancel Transaction]              [Complete Sale]              │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Sales Records List

```
┌─────────────────────────────────────────────────────────────────┐
│  Sales Records                                    [+ New Sale]  │
├─────────────────────────────────────────────────────────────────┤
│  Date: [05/01/2026] to [05/05/2026]  Employee: [All ▼]         │
│  Customer: [____________]  Payment: [☑Cash ☑Card ☑Account]     │
├─────────────────────────────────────────────────────────────────┤
│  Date       │ Transaction ID │ Customer    │ Employee │ Total   │
├─────────────┼────────────────┼─────────────┼──────────┼─────────┤
│  05/05 2:30p│ TXN-00001234   │ John Doe    │ J.Smith  │ $140.69 │
│  05/05 1:15p│ TXN-00001233   │ Walk-in     │ M.Jones  │  $49.99 │
│  05/05 11:00│ TXN-00001232   │ Jane Smith  │ J.Smith  │ $234.50 │
├─────────────────────────────────────────────────────────────────┤
│  Period Total: $425.18 (3 transactions)                        │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Transaction Detail View

```
┌─────────────────────────────────────────────────────────────────┐
│  Transaction: TXN-00001234                              [Print] │
├─────────────────────────────────────────────────────────────────┤
│  Date: May 5, 2026 2:30 PM                                     │
│  Employee: Jane Smith                                          │
│  Customer: John Doe (john.doe@email.com)                       │
│  Payment: Credit Card                                          │
├─────────────────────────────────────────────────────────────────┤
│  ITEMS                                                         │
│  ─────────────────────────────────────────────────────────────  │
│  1× Clean Code (978-0-13-235088-4)              $49.99         │
│  2× JavaScript Guide (978-0-59-651798-1)        $79.98         │
│  ─────────────────────────────────────────────────────────────  │
│                                     Subtotal:   $129.97        │
│                                     Tax:         $10.72        │
│                                     TOTAL:      $140.69        │
├─────────────────────────────────────────────────────────────────┤
│  Inventory updated: 3 books decremented                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/sales | Create new sale transaction |
| GET | /api/sales | List sales with filters |
| GET | /api/sales/{id} | Get transaction details |
| GET | /api/sales/reports/daily | Daily summary report |
| GET | /api/sales/reports/weekly | Weekly summary report |
| GET | /api/sales/reports/monthly | Monthly summary report |
| GET | /api/sales/reports/bestsellers | Best-selling books |

---

## 6. Request/Response Schemas

```python
# backend/app/schemas/sales.py

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from enum import Enum

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    ACCOUNT = "account"

class SaleLineItemCreate(BaseModel):
    book_id: UUID
    quantity: int
    unit_price: Decimal

class SaleCreate(BaseModel):
    customer_id: Optional[UUID] = None
    line_items: List[SaleLineItemCreate]
    payment_method: PaymentMethod
    discount_amount: Decimal = Decimal("0.00")

class SaleLineItemResponse(BaseModel):
    book_id: UUID
    book_title: str
    book_isbn: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal

class SaleResponse(BaseModel):
    id: UUID
    transaction_number: str
    customer_id: Optional[UUID]
    customer_name: Optional[str]
    employee_id: UUID
    employee_name: str
    line_items: List[SaleLineItemResponse]
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total: Decimal
    payment_method: PaymentMethod
    created_at: datetime

class SalesSearchParams(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    customer_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    book_id: Optional[UUID] = None
    payment_method: Optional[PaymentMethod] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    page: int = 1
    per_page: int = 25

class DailySummary(BaseModel):
    date: datetime
    transaction_count: int
    total_revenue: Decimal
    average_transaction: Decimal
    by_payment_method: dict
```

---

## 7. Transaction Processing

### 7.1 Atomic Transaction Flow

```python
# backend/app/services/sales_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

class SalesService:
    async def process_sale(
        self, 
        db: AsyncSession, 
        sale_data: SaleCreate,
        employee_id: UUID
    ) -> SaleResponse:
        async with db.begin():  # Transaction block
            # 1. Validate stock availability
            for item in sale_data.line_items:
                available = await self.check_stock(db, item.book_id)
                if available < item.quantity:
                    raise InsufficientStockError(item.book_id)
            
            # 2. Create sales transaction record
            sale = SalesTransaction(
                employee_id=employee_id,
                customer_id=sale_data.customer_id,
                payment_method=sale_data.payment_method,
                discount_amount=sale_data.discount_amount,
            )
            db.add(sale)
            await db.flush()  # Get sale.id
            
            # 3. Create line items
            subtotal = Decimal("0.00")
            for item in sale_data.line_items:
                line = SalesLineItem(
                    transaction_id=sale.id,
                    book_id=item.book_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                db.add(line)
                subtotal += item.quantity * item.unit_price
            
            # 4. Calculate totals
            sale.subtotal = subtotal
            sale.tax_amount = self.calculate_tax(subtotal)
            sale.total = subtotal + sale.tax_amount - sale.discount_amount
            
            # 5. Decrement inventory (same transaction)
            for item in sale_data.line_items:
                await self.decrement_inventory(
                    db, item.book_id, item.quantity
                )
            
            # 6. Generate transaction number
            sale.transaction_number = await self.generate_txn_number(db)
            
            await db.commit()
            return sale
```

### 7.2 Inventory Update

```python
async def decrement_inventory(
    self, db: AsyncSession, book_id: UUID, quantity: int
):
    # Update inventory, preferring warehouse with most stock
    result = await db.execute(
        update(Inventory)
        .where(Inventory.book_id == book_id)
        .where(Inventory.quantity >= quantity)
        .values(quantity=Inventory.quantity - quantity)
        .returning(Inventory.id)
    )
    if not result.scalar():
        raise InsufficientStockError(book_id)
```

---

## 8. Reporting Service

```python
class ReportingService:
    async def get_daily_summary(
        self, db: AsyncSession, date: datetime
    ) -> DailySummary:
        query = """
            SELECT 
                COUNT(*) as transaction_count,
                COALESCE(SUM(total), 0) as total_revenue,
                COALESCE(AVG(total), 0) as average_transaction
            FROM sales_transactions
            WHERE DATE(created_at) = :date
        """
        result = await db.execute(query, {"date": date})
        row = result.fetchone()
        
        # Payment method breakdown
        payment_query = """
            SELECT payment_method, SUM(total) as amount
            FROM sales_transactions
            WHERE DATE(created_at) = :date
            GROUP BY payment_method
        """
        payments = await db.execute(payment_query, {"date": date})
        
        return DailySummary(
            date=date,
            transaction_count=row.transaction_count,
            total_revenue=row.total_revenue,
            average_transaction=row.average_transaction,
            by_payment_method={r.payment_method: r.amount for r in payments}
        )
    
    async def get_bestsellers(
        self, db: AsyncSession, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 10
    ) -> List[dict]:
        query = """
            SELECT 
                b.id, b.title, b.author,
                SUM(sl.quantity) as units_sold,
                SUM(sl.quantity * sl.unit_price) as revenue
            FROM sales_line_items sl
            JOIN books b ON b.id = sl.book_id
            JOIN sales_transactions st ON st.id = sl.transaction_id
            WHERE st.created_at BETWEEN :start_date AND :end_date
            GROUP BY b.id, b.title, b.author
            ORDER BY units_sold DESC
            LIMIT :limit
        """
        return await db.execute(query, {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit
        })
```

---

## 9. Testing Requirements

| Test Case | Description | Type |
|-----------|-------------|------|
| SALE-001 | Process sale creates transaction record | Integration |
| SALE-002 | Inventory decremented atomically | Integration |
| SALE-003 | Insufficient stock prevents sale | Unit |
| SALE-004 | Tax calculation is correct | Unit |
| SALE-005 | Search filters work correctly | Integration |
| SALE-006 | Daily report aggregates correctly | Integration |
| SALE-007 | Bestseller report sorted correctly | Integration |
| SALE-008 | Only admin/employee can process | Security |

---

## Next Document: [06-PURCHASE-ORDERS.md](06-PURCHASE-ORDERS.md)
