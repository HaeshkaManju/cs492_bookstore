# Revised System Architecture

**Version:** 2.0 (Flask-based)  
**Updated:** 2026-05-05  
**Changes:** Flask instead of FastAPI, Invoice model, Book requests

---

## 1. Technology Stack (Revised)

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Web Framework** | Flask 3.x | Simpler, template-native, widely taught |
| **Templates** | Jinja2 | Built into Flask, server-side rendering |
| **Database** | PostgreSQL 15+ | ACID compliance, relational integrity |
| **ORM** | SQLAlchemy 2.x | Python standard, Flask-SQLAlchemy integration |
| **Migrations** | Flask-Migrate (Alembic) | Version-controlled schema changes |
| **Auth** | Flask-Login + JWT | Session + API token support |
| **Forms** | Flask-WTF | CSRF protection, validation |
| **Testing** | pytest + pytest-flask | Flask-native testing |
| **Frontend JS** | Vanilla JS / HTMX | Minimal, progressive enhancement |
| **CSS** | Bootstrap 5 | Quick prototyping, responsive |

---

## 2. Project Structure (Flask)

```
bookstore/
├── app/
│   ├── __init__.py              # Application factory
│   ├── extensions.py            # Flask extensions init
│   ├── config.py                # Configuration classes
│   │
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── inventory.py
│   │   ├── invoice.py
│   │   ├── book_request.py
│   │   └── purchase_order.py
│   │
│   ├── blueprints/              # Route modules
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── inventory/
│   │   ├── sales/
│   │   ├── orders/
│   │   └── customer/
│   │
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── inventory_service.py
│   │   ├── invoice_service.py
│   │   └── request_service.py
│   │
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── inventory/
│   │   ├── invoices/
│   │   └── customer/
│   │
│   ├── static/                  # CSS, JS, images
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   │
│   └── utils/                   # Helpers
│       ├── __init__.py
│       ├── decorators.py        # @admin_required, etc.
│       ├── validators.py
│       └── pdf_generator.py     # Invoice PDF
│
├── migrations/                  # Alembic migrations
├── tests/                       # Test suite
├── instance/                    # Instance-specific config (gitignored)
├── .env.example                 # Environment template
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── run.py                       # Application entry point
```

---

## 3. Business Model Changes

### 3.1 Invoice System (Replaces Payment Processing)

```
┌─────────────────────────────────────────────────────────────────┐
│                        INVOICE                                   │
├─────────────────────────────────────────────────────────────────┤
│  Invoice #: INV-2026-001234                                     │
│  Date: May 5, 2026                                              │
│  Status: DRAFT | SENT | PAID | CANCELLED                        │
│                                                                 │
│  Bill To:                                                       │
│    John Smith                                                   │
│    123 Collector Lane                                           │
│    Rare Book City, ST 12345                                     │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  ITEMS IN STOCK                                                 │
│  Description                    Condition    Qty    Price       │
│  "Moby Dick" 1st Ed (1851)     Very Good     1    $2,500.00    │
│  "The Great Gatsby" (1925)     Fine          1    $8,000.00    │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  PENDING REQUESTS                                               │
│  "To Kill a Mockingbird"       Fine          1    TBD          │
│    → When available in requested condition, we will notify you  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                    Subtotal:    $10,500.00      │
│                                    (Pending items not included) │
│                                                                 │
│  Payment Terms: Net 30                                          │
│  Notes: _________________________________________________       │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Book Request System

**Request States:**
```
PENDING → MATCHED → NOTIFIED → FULFILLED
                  ↘ EXPIRED (after 1 year)
                  ↘ CANCELLED (by customer)
```

**Matching Logic:**
- When new book added to inventory, check pending requests
- Match on: ISBN (if available), Title, Author, Condition level
- Condition levels: Fine ≥ Very Good ≥ Good ≥ Fair ≥ Poor
- Customer requesting "Good" will match "Good", "Very Good", or "Fine"

### 3.3 Condition Grading

| Grade | Description | Code |
|-------|-------------|------|
| Fine (F) | As new, no defects | 5 |
| Very Good (VG) | Minor wear, no major defects | 4 |
| Good (G) | Average used, all pages present | 3 |
| Fair (FR) | Heavy wear, but complete | 2 |
| Poor (P) | Reading copy only | 1 |

---

## 4. Data Model Updates

### 4.1 New: BOOK_REQUEST Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| customer_id | UUID | FK → CUSTOMER |
| isbn | VARCHAR(17) | Optional ISBN |
| title | VARCHAR(500) | Requested title |
| author | VARCHAR(255) | Author name |
| min_condition | INTEGER | Minimum acceptable (1-5) |
| max_price | DECIMAL | Budget limit (optional) |
| status | ENUM | pending, matched, notified, fulfilled, expired, cancelled |
| matched_book_id | UUID | FK → BOOK (when matched) |
| notes | TEXT | Customer notes |
| created_at | TIMESTAMP | Request date |
| expires_at | TIMESTAMP | Auto-expire date |

### 4.2 Updated: INVOICE Table (was ORDER)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| invoice_number | VARCHAR(20) | INV-YYYY-NNNNNN |
| customer_id | UUID | FK → CUSTOMER |
| status | ENUM | draft, sent, paid, cancelled |
| subtotal | DECIMAL | Total of available items |
| notes | TEXT | Invoice notes |
| payment_terms | VARCHAR(50) | "Net 30", etc. |
| created_at | TIMESTAMP | Creation date |
| sent_at | TIMESTAMP | When sent to customer |
| paid_at | TIMESTAMP | Payment received |
| created_by | UUID | FK → USER (employee) |

### 4.3 New: INVOICE_LINE Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| invoice_id | UUID | FK → INVOICE |
| line_type | ENUM | 'item' or 'request' |
| book_id | UUID | FK → BOOK (for items) |
| request_id | UUID | FK → BOOK_REQUEST (for pending) |
| description | TEXT | Line description |
| condition | INTEGER | Book condition (1-5) |
| quantity | INTEGER | Always 1 for rare books |
| unit_price | DECIMAL | Price (NULL for requests) |
| is_pending | BOOLEAN | True if request, not available item |

---

## 5. Flask Blueprint Structure

```python
# app/__init__.py

from flask import Flask
from app.extensions import db, migrate, login_manager, csrf

def create_app(config_name='development'):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.inventory import inventory_bp
    from app.blueprints.sales import sales_bp
    from app.blueprints.customer import customer_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(sales_bp, url_prefix='/sales')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    
    return app
```

---

## 6. Authentication (Flask-Login)

```python
# app/utils/decorators.py

from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """Decorator to require specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required('admin')(f)

def staff_required(f):
    return role_required('admin', 'employee')(f)
```

---

## 7. Key Differences Summary

| Aspect | FastAPI Version | Flask Version |
|--------|-----------------|---------------|
| Routing | Decorators on functions | Blueprints |
| Templates | Separate React app | Jinja2 integrated |
| Forms | Pydantic schemas | Flask-WTF |
| Auth | JWT only | Flask-Login + optional JWT |
| Async | Native async/await | Sync (simpler for learning) |
| API Docs | Auto-generated Swagger | Manual or flask-apispec |
| Payments | Tokenized payments | Invoice generation |
| Orders | Immediate fulfillment | Request + notification system |

---

## 8. Updated Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                         │
│                   Flask + Jinja2 Templates                       │
├─────────────────────────────┬───────────────────────────────────┤
│     Admin/Employee Portal   │      Customer Portal              │
│  (inventory, sales, POs)    │  (browse, request, invoices)      │
└─────────────────────────────┴───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│                         Flask App                                │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│  Auth       │  Inventory  │  Invoice    │  Request              │
│  Service    │  Service    │  Service    │  Service              │
└─────────────┴─────────────┴─────────────┴───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│              PostgreSQL + SQLAlchemy ORM                         │
├───────────┬───────────┬───────────┬───────────┬─────────────────┤
│  Users    │  Books    │ Invoices  │ Requests  │  Purchase       │
│  Roles    │ Inventory │  Lines    │           │  Orders         │
└───────────┴───────────┴───────────┴───────────┴─────────────────┘
```

---

## Next: Sprint 1 Task Outlines
