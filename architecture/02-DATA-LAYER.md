# Data Layer Architecture

**Related Stories:** US-002, US-011  
**Related Tasks:** S1-9 to S1-14

---

## 1. Overview

The data layer provides persistent storage for all system entities with:
- Relational integrity via foreign keys
- ACID-compliant transactions
- Automated backup and recovery
- Version-controlled migrations

---

## 2. Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    USER     │       │   CUSTOMER  │       │   ADDRESS   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ user_id(FK) │       │ id (PK)     │
│ email       │       │ id (PK)     │───────│ street      │
│ password    │       │ shipping_   │       │ city        │
│ role        │       │ address_id  │       │ state       │
│ created_at  │       │ billing_    │       │ zip         │
└─────────────┘       │ address_id  │       │ country     │
                      └─────────────┘       └─────────────┘
                             │
                             │ 1:*
                             ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    BOOK     │       │    ORDER    │       │ ORDER_LINE  │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │◄──────│ order_id(FK)│
│ isbn        │       │ customer_id │       │ book_id(FK) │
│ title       │◄──────│ status      │       │ quantity    │
│ author      │       │ total       │       │ unit_price  │
│ publisher   │       │ created_at  │       └─────────────┘
│ mfr_price   │       └─────────────┘
│ list_price  │
│ category    │
└─────────────┘
      │
      │ 1:*
      ▼
┌─────────────┐       ┌─────────────┐
│  INVENTORY  │       │  WAREHOUSE  │
├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │
│ book_id(FK) │◄──────│ name        │
│ warehouse_id│       │ location    │
│ quantity    │       │ capacity    │
│ reorder_lvl │       └─────────────┘
└─────────────┘

┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│SALES_TRANS  │       │ SALES_LINE  │       │MANUFACTURER │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ txn_id (FK) │       │ id (PK)     │
│ customer_id │       │ book_id(FK) │       │ name        │
│ employee_id │       │ quantity    │       │ contact     │
│ subtotal    │       │ unit_price  │       │ email       │
│ tax         │       └─────────────┘       │ address_id  │
│ total       │                             └─────────────┘
│ payment_mth │                                    │
│ created_at  │                                    │ 1:*
└─────────────┘                                    ▼
                                           ┌─────────────┐
┌─────────────┐       ┌─────────────┐      │PURCHASE_ORD │
│   PO_LINE   │       │  PO_STATUS  │      ├─────────────┤
├─────────────┤       ├─────────────┤      │ id (PK)     │
│ po_id (FK)  │◄──────│ DRAFT       │      │ mfr_id (FK) │
│ book_id(FK) │       │ SUBMITTED   │      │ status      │
│ quantity    │       │ SHIPPED     │      │ created_at  │
│ unit_cost   │       │ RECEIVED    │      │ received_at │
└─────────────┘       │ CANCELLED   │      │ total       │
                      └─────────────┘      └─────────────┘
```

---

## 3. Table Specifications

### 3.1 USER Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Primary identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Login credential |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed |
| role | ENUM | NOT NULL | 'admin', 'employee', 'customer' |
| first_name | VARCHAR(100) | NOT NULL | Display name |
| last_name | VARCHAR(100) | NOT NULL | Display name |
| is_active | BOOLEAN | DEFAULT TRUE | Soft delete flag |
| created_at | TIMESTAMP | DEFAULT NOW() | Audit field |
| updated_at | TIMESTAMP | ON UPDATE | Audit field |

> **Task Reference:** S1-9 (Design ERD), S1-15 (Roles matrix)

### 3.2 BOOK Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Primary identifier |
| isbn | VARCHAR(17) | UNIQUE, NOT NULL | ISBN-10 or ISBN-13 |
| title | VARCHAR(500) | NOT NULL | Book title |
| author | VARCHAR(255) | NOT NULL | Author name(s) |
| publisher | VARCHAR(255) | | Publisher name |
| mfr_price | DECIMAL(10,2) | NOT NULL | Cost from manufacturer |
| list_price | DECIMAL(10,2) | NOT NULL | Customer sale price |
| category | VARCHAR(100) | | Genre/category |
| description | TEXT | | Book description |
| is_active | BOOLEAN | DEFAULT TRUE | Available for sale |
| created_at | TIMESTAMP | DEFAULT NOW() | Audit field |

> **Validation (S1-11):** ISBN must match format `^(97[89])?\d{9}[\dX]$`

### 3.3 INVENTORY Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Primary identifier |
| book_id | UUID | FK → BOOK | Book reference |
| warehouse_id | UUID | FK → WAREHOUSE | Location |
| quantity | INTEGER | NOT NULL, >= 0 | Current stock |
| reorder_level | INTEGER | DEFAULT 10 | Low-stock threshold |
| created_at | TIMESTAMP | DEFAULT NOW() | Audit field |
| updated_at | TIMESTAMP | ON UPDATE | Audit field |

**Unique Constraint:** (book_id, warehouse_id)

### 3.4 SALES_TRANSACTION Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Primary identifier |
| customer_id | UUID | FK → CUSTOMER | NULL for walk-in |
| employee_id | UUID | FK → USER | Processing employee |
| subtotal | DECIMAL(10,2) | NOT NULL | Pre-tax amount |
| tax_amount | DECIMAL(10,2) | NOT NULL | Calculated tax |
| total | DECIMAL(10,2) | NOT NULL | Final amount |
| payment_method | ENUM | NOT NULL | 'cash', 'card', 'account' |
| created_at | TIMESTAMP | DEFAULT NOW() | Transaction time |

### 3.5 ORDER Table (Customer Orders)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Primary identifier |
| customer_id | UUID | FK → CUSTOMER | NOT NULL |
| status | ENUM | NOT NULL | 'pending', 'processing', 'shipped', 'delivered', 'cancelled' |
| shipping_address_id | UUID | FK → ADDRESS | Delivery address |
| subtotal | DECIMAL(10,2) | NOT NULL | Items total |
| shipping_cost | DECIMAL(10,2) | DEFAULT 0 | Shipping fee |
| tax_amount | DECIMAL(10,2) | NOT NULL | Tax |
| total | DECIMAL(10,2) | NOT NULL | Final amount |
| created_at | TIMESTAMP | DEFAULT NOW() | Order placement |
| updated_at | TIMESTAMP | ON UPDATE | Status changes |

### 3.6 PURCHASE_ORDER Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Primary identifier |
| manufacturer_id | UUID | FK → MANUFACTURER | Supplier |
| status | ENUM | NOT NULL | 'draft', 'submitted', 'shipped', 'received', 'cancelled' |
| total | DECIMAL(10,2) | NOT NULL | Order total |
| created_by | UUID | FK → USER | Employee who created |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| submitted_at | TIMESTAMP | NULL | Submission time |
| received_at | TIMESTAMP | NULL | Receipt time |

---

## 4. Data Integrity Rules

### 4.1 Transactional Operations

| Operation | Tables Affected | Transaction Requirement |
|-----------|-----------------|------------------------|
| Process Sale | SALES_TRANSACTION, SALES_LINE, INVENTORY | Atomic: all or nothing |
| Receive PO | PURCHASE_ORDER, INVENTORY | Atomic: status + quantity |
| Customer Order | ORDER, ORDER_LINE, INVENTORY | Reserve inventory atomically |

> **Reference:** US-011 (Data Backup and Integrity System)

### 4.2 Validation Rules (S1-11)

| Field | Validation Rule |
|-------|-----------------|
| email | RFC 5322 format |
| isbn | ISBN-10 or ISBN-13 checksum valid |
| quantity | Integer >= 0 |
| price | Decimal > 0 |
| password | Min 8 chars, 1 upper, 1 lower, 1 number |

---

## 5. SQLAlchemy Models

```python
# backend/app/models/book.py

from sqlalchemy import Column, String, Numeric, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class Book(Base):
    __tablename__ = "books"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    isbn = Column(String(17), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    publisher = Column(String(255))
    mfr_price = Column(Numeric(10, 2), nullable=False)
    list_price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    inventory_items = relationship("Inventory", back_populates="book")
    sales_lines = relationship("SalesLine", back_populates="book")
    order_lines = relationship("OrderLine", back_populates="book")
```

---

## 6. Migration Strategy

### 6.1 Tools
- **Alembic** for version-controlled migrations
- Migration scripts stored in `backend/alembic/versions/`

### 6.2 Migration Workflow (S1-12)
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

---

## 7. Backup Strategy (US-011)

| Component | Strategy | Frequency |
|-----------|----------|-----------|
| Full Backup | pg_dump to encrypted storage | Daily at 02:00 UTC |
| WAL Archiving | Continuous | Real-time |
| Retention | 30 days | Rolling |
| RPO | 1 hour maximum data loss | |
| RTO | 4 hours maximum downtime | |

---

## Next Document: [03-AUTHENTICATION.md](03-AUTHENTICATION.md)
