# System Overview

**Related Stories:** US-001, US-004  
**Related Tasks:** S1-1 to S1-8, S2-1 to S2-5

---

## 1. Project Vision

A rare bookstore owner requires an automated system to replace paper-based processes for:
- Accounting and inventory tracking
- Sales recording and reporting
- Manufacturer ordering
- Customer order placement

This is fundamentally a **CRUD application** with role-based access control and multiple user interfaces.

---

## 2. Core Capabilities

| Capability | Description | Definition of Done Reference |
|------------|-------------|------------------------------|
| **Inventory Management** | Track books across warehouses | DoD Section 4.1 |
| **Sales Records** | Record and report transactions | DoD Section 4.2 |
| **Purchase Orders** | Order books from manufacturers | DoD Section 4.3 |
| **Customer Portal** | Public interface for customers | DoD Section 4.4 |

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                         │
├─────────────────────────────┬───────────────────────────────────┤
│     Admin/Employee Portal   │         Customer Portal           │
│  (Flask, Flask SQL Alchemy) │    (Flask, Flask SQL Alchemy)     │
└─────────────────────────────┴───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│                    Python / FastAPI                              │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│  Auth       │  Inventory  │   Sales     │   Orders              │
│  Service    │  Service    │   Service   │   Service             │
└─────────────┴─────────────┴─────────────┴───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│                       PostgreSQL                                 │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│   Users     │   Books     │   Sales     │   Orders              │
│   Roles     │   Inventory │   Txns      │   POs                 │
└─────────────┴─────────────┴─────────────┴───────────────────────┘
```

---

## 4. Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Frontend** | React.js + TypeScript | Component-based, type-safe, wide adoption |
| **Backend** | Python + FastAPI | Async support, auto-docs, type hints |
| **Database** | PostgreSQL | ACID compliance, relational integrity |
| **Auth** | JWT + bcrypt | Stateless auth, secure password storage |
| **ORM** | SQLAlchemy | Python-native, migration support |
| **Testing** | pytest + pytest-cov | Python standard, coverage reporting |
| **CI/CD** | GitHub Actions | Integrated with repository (S1-8) |
| **Containers** | Docker | Consistent dev/prod environments |

---

## 5. System Actors

| Actor | Description | Access Level |
|-------|-------------|--------------|
| **Admin** | Store owner/manager | Full system access |
| **Employee** | Store staff | Limited admin (sales, inventory view) |
| **Customer** | Public user | Portal access only |
| **Manufacturer** | External entity | Receives POs (no system access) |

---

## 6. Project Structure

```
bookstore-inventory/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── inventory.py
│   │   │   │   ├── sales.py
│   │   │   │   ├── orders.py
│   │   │   │   └── customers.py
│   │   │   └── dependencies.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── book.py
│   │   │   ├── inventory.py
│   │   │   ├── sales.py
│   │   │   └── order.py
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   └── main.py
│   ├── tests/
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   └── package.json
├── database/
│   └── migrations/
├── docs/
└── docker-compose.yml
```

> **Reference:** S1-2 (Set up project folder structure)

---

## 7. Non-Functional Requirements Summary

| Requirement | Target | Reference |
|-------------|--------|-----------|
| Page load time | < 2 seconds | US-010 |
| API response | < 500ms (95th percentile) | US-010 |
| Concurrent users | 50 minimum | US-010 |
| Backup frequency | Daily automated | US-011 |
| Recovery time | 4 hours maximum | US-011 |

---

## 8. Module Dependencies

```
Authentication ──────────────┐
                             │
Inventory ◄──────────────────┼───► Sales
    │                        │        │
    │                        │        │
    ▼                        │        ▼
Purchase Orders              │    Sales Records
                             │
Customer Portal ◄────────────┘
```

All modules depend on Authentication for access control.  
Sales and Inventory are bidirectionally linked (sales decrement inventory).  
Purchase Orders increment Inventory upon receipt.

---

## Next Document: [02-DATA-LAYER.md](02-DATA-LAYER.md)
