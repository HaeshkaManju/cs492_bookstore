# Bookstore API Integration Guide

## A Complete Beginner's Guide to Using the Bookstore API

---

## Table of Contents

1. [Introduction - What is an API?](#1-introduction---what-is-an-api)
2. [How This Codebase is Organized](#2-how-this-codebase-is-organized)
3. [Understanding the Design Patterns](#3-understanding-the-design-patterns)
4. [Getting Started](#4-getting-started)
5. [Working with Services](#5-working-with-services)
6. [Working with Repositories](#6-working-with-repositories)
7. [Working with Schemas (DTOs)](#7-working-with-schemas-dtos)
8. [Working with Models](#8-working-with-models)
9. [Complete Code Examples](#9-complete-code-examples)
10. [Adding RBAC (Role-Based Access Control)](#10-adding-rbac-role-based-access-control)
11. [Error Handling](#11-error-handling)
12. [Testing Your Code](#12-testing-your-code)
13. [Common Mistakes and How to Avoid Them](#13-common-mistakes-and-how-to-avoid-them)
14. [Glossary of Terms](#14-glossary-of-terms)

---

## 1. Introduction - What is an API?

### What is an API?

API stands for **Application Programming Interface**. Think of it like a waiter in a restaurant:

- You (the customer) don't go into the kitchen to cook your own food
- Instead, you tell the waiter what you want
- The waiter goes to the kitchen, gets your food, and brings it back

An API works the same way:
- Your code doesn't directly access the database
- Instead, you call API functions that do the work for you
- The API handles all the complex operations and returns the results

### Why Do We Use APIs?

1. **Simplicity**: You don't need to know HOW something works, just how to ASK for it
2. **Safety**: The API prevents you from accidentally breaking things
3. **Consistency**: Everyone uses the same way to do things
4. **Modularity**: Different parts of the system can be developed independently

### What is This Bookstore API?

This is a **Python Flask** application for managing a rare bookstore. It handles:

- **Users**: Customer accounts, employee accounts, admin accounts
- **Books**: The catalog of books for sale
- **Inventory**: How many copies of each book we have, in what condition
- **Invoices**: Bills we send to customers
- **Book Requests**: When customers want a book we don't have
- **Purchase Orders**: Orders we send to suppliers

---

## 2. How This Codebase is Organized

### Folder Structure Explained

```
bookstore/
├── app/                      # All application code lives here
│   ├── __init__.py          # Creates the Flask application
│   ├── config.py            # Settings (database URL, etc.)
│   ├── extensions.py        # Flask extensions (database, login, etc.)
│   │
│   ├── models/              # DATABASE TABLES as Python classes
│   │   ├── __init__.py      # Exports all models
│   │   ├── base.py          # Base class with common features
│   │   ├── user.py          # User accounts
│   │   ├── customer.py      # Customer profiles + addresses
│   │   ├── book.py          # Book catalog
│   │   ├── inventory.py     # Stock levels + warehouses
│   │   ├── invoice.py       # Customer invoices
│   │   ├── book_request.py  # Book requests from customers
│   │   └── purchase_order.py # Orders to suppliers
│   │
│   ├── repositories/        # DATABASE ACCESS LAYER
│   │   ├── __init__.py      # Exports all repositories
│   │   ├── base.py          # Base repository with CRUD operations
│   │   ├── user_repository.py
│   │   ├── customer_repository.py
│   │   ├── book_repository.py
│   │   ├── inventory_repository.py
│   │   ├── invoice_repository.py
│   │   ├── book_request_repository.py
│   │   └── purchase_order_repository.py
│   │
│   ├── services/            # BUSINESS LOGIC LAYER
│   │   ├── __init__.py      # Exports all services
│   │   ├── base.py          # Base service with common features
│   │   ├── user_service.py
│   │   ├── customer_service.py
│   │   ├── book_service.py
│   │   ├── inventory_service.py
│   │   ├── invoice_service.py
│   │   ├── book_request_service.py
│   │   └── purchase_order_service.py
│   │
│   ├── schemas/             # DATA TRANSFER OBJECTS (DTOs)
│   │   ├── __init__.py      # Exports all schemas
│   │   ├── base.py          # Base schema class
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── book.py
│   │   ├── inventory.py
│   │   ├── invoice.py
│   │   ├── book_request.py
│   │   └── purchase_order.py
│   │
│   ├── api/                 # API INTEGRATION LAYER
│   │   ├── __init__.py      # Service factories + response helpers
│   │   └── hooks.py         # Integration hooks for RBAC
│   │
│   └── utils/               # UTILITY FUNCTIONS
│       └── validators.py    # Input validation
│
├── tests/                   # TEST FILES
│   ├── conftest.py         # Test fixtures
│   ├── test_models.py      # Model tests
│   ├── test_services.py    # Service tests
│   └── test_validators.py  # Validator tests
│
├── migrations/             # DATABASE MIGRATIONS
├── docs/                   # DOCUMENTATION (you are here!)
├── run.py                  # Application entry point
└── requirements.txt        # Python dependencies
```

### What Each Layer Does

Think of the application like a building with floors:

```
┌─────────────────────────────────────────────────────┐
│                   YOUR CODE                          │  ← You write code here
│              (Flask routes, views)                   │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                    SERVICES                          │  ← Business logic
│     (BookService, InvoiceService, etc.)             │    "WHAT to do"
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                  REPOSITORIES                        │  ← Data access
│   (BookRepository, InvoiceRepository, etc.)         │    "HOW to get data"
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                    MODELS                            │  ← Database tables
│        (Book, Invoice, User, etc.)                  │    "WHAT data looks like"
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                   DATABASE                           │  ← Actual storage
│                 (PostgreSQL)                         │
└─────────────────────────────────────────────────────┘
```

**Rule**: Each layer ONLY talks to the layer directly below it.

---

## 3. Understanding the Design Patterns

### What is a Design Pattern?

A design pattern is a **proven solution** to a common problem. It's like a recipe - you don't have to invent a new way to make a cake every time, you follow a recipe that works.

### Patterns Used in This Application

#### 1. Repository Pattern

**Problem**: We need to get data from the database, but we don't want database code scattered everywhere.

**Solution**: Create a "Repository" class that handles ALL database operations for one type of data.

**Example**:
```python
# WITHOUT Repository Pattern (BAD - database code everywhere)
def get_books_for_homepage():
    books = db.session.query(Book).filter(Book.is_active == True).all()
    return books

def get_books_for_search(query):
    books = db.session.query(Book).filter(Book.title.ilike(f'%{query}%')).all()
    return books

# WITH Repository Pattern (GOOD - all database code in one place)
class BookRepository:
    def get_active(self):
        return Book.query.filter_by(is_active=True).all()
    
    def search(self, query):
        return Book.query.filter(Book.title.ilike(f'%{query}%')).all()

# Then use it like this:
book_repo = BookRepository()
books = book_repo.search("Python")
```

#### 2. Service Layer Pattern

**Problem**: Business logic (rules like "you can't sell more books than you have") shouldn't be mixed with database code.

**Solution**: Create a "Service" class that contains business logic and uses repositories for data access.

**Example**:
```python
# The Service handles business logic
class InventoryService:
    def __init__(self):
        self.repository = InventoryRepository()
    
    def reserve_for_sale(self, inventory_id, quantity):
        # Get the inventory record
        inventory = self.repository.get_by_id(inventory_id)
        
        # BUSINESS RULE: Can't sell more than we have
        if quantity > inventory.quantity:
            raise ValidationError(["Not enough stock!"])
        
        # Update the quantity
        inventory.quantity -= quantity
        self.repository.commit()
        
        return inventory
```

#### 3. Data Transfer Object (DTO) Pattern

**Problem**: We don't want to expose our database models directly to the outside world. What if the model changes?

**Solution**: Create "Schema" classes that define exactly what data goes in and out.

**Example**:
```python
# The Model (internal - might have sensitive data)
class User:
    id = ...
    email = ...
    password_hash = ...  # We NEVER want to expose this!
    first_name = ...
    last_name = ...

# The Schema (external - safe to share)
class UserSchema:
    id: UUID
    email: str
    first_name: str
    last_name: str
    # Notice: NO password_hash!
    
    @classmethod
    def from_model(cls, user):
        return cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name
        )
```

#### 4. Factory Pattern

**Problem**: We need a consistent way to create service instances.

**Solution**: Create "factory functions" that return service instances.

**Example**:
```python
# In app/api/__init__.py
from functools import lru_cache

@lru_cache(maxsize=1)  # This caches the instance - only creates one!
def get_book_service():
    return BookService()

# Then use it anywhere:
from app.api import get_book_service

book_service = get_book_service()
books = book_service.search("Python")
```

---

## 4. Getting Started

### Step 1: Set Up Your Environment

Before you can run any code, you need to set up your development environment.

```bash
# 1. Navigate to the bookstore folder
cd bookstore

# 2. Create a virtual environment (isolates your Python packages)
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 4. Install required packages
pip install -r requirements.txt

# 5. Copy the example environment file
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Mac/Linux

# 6. Edit .env with your database settings
# Open .env in a text editor and set DATABASE_URL
```

### Step 2: Set Up the Database

```bash
# Initialize the migrations folder (first time only)
flask db init

# Create the database tables
flask db migrate -m "Initial schema"
flask db upgrade
```

### Step 3: Test That Everything Works

```bash
# Start the Flask shell (interactive Python with app loaded)
flask shell

# In the shell, try:
>>> from app.models import Book
>>> from app.services import BookService
>>> book_service = BookService()
>>> print("Success! The application is set up correctly.")
```

---

## 5. Working with Services

Services are your **main interface** for doing things. They contain all the business logic.

### Available Services

| Service | Purpose | Import |
|---------|---------|--------|
| `UserService` | Manage user accounts | `from app.services import UserService` |
| `CustomerService` | Manage customers + addresses | `from app.services import CustomerService` |
| `BookService` | Manage book catalog | `from app.services import BookService` |
| `InventoryService` | Manage stock levels | `from app.services import InventoryService` |
| `InvoiceService` | Create and manage invoices | `from app.services import InvoiceService` |
| `BookRequestService` | Handle customer book requests | `from app.services import BookRequestService` |
| `PurchaseOrderService` | Manage orders to suppliers | `from app.services import PurchaseOrderService` |

### How to Use Services

#### Method 1: Create Directly

```python
from app.services import BookService

# Create a service instance
book_service = BookService()

# Use the service
book = book_service.create_book(
    title="Clean Code",
    author="Robert C. Martin",
    isbn="978-0-13-235088-4",
    category="Programming"
)

print(f"Created book: {book.title} with ID: {book.id}")
```

#### Method 2: Use Factory Functions (Recommended)

```python
from app.api import get_book_service

# Get a cached service instance
book_service = get_book_service()

# Use the service
books = book_service.search("Python")
print(f"Found {len(books['items'])} books")
```

### Service Methods Reference

#### BookService Methods

```python
from app.api import get_book_service

book_service = get_book_service()

# CREATE a new book
book = book_service.create_book(
    title="The Pragmatic Programmer",    # Required
    author="David Thomas",               # Required
    isbn="978-0-13-595705-9",           # Optional
    publisher="Addison-Wesley",          # Optional
    year_published=2019,                 # Optional
    description="A guide to...",         # Optional
    category="Programming",              # Optional
    auto_commit=True                     # Default: True, commits to database
)

# READ - Get book by ID
from uuid import UUID
book = book_service.get_by_id(UUID("your-book-id-here"))

# READ - Get book by ISBN
book = book_service.get_by_isbn("978-0-13-595705-9")

# READ - Search books
results = book_service.search(
    query="Python",           # Search term
    category="Programming",   # Optional filter
    in_stock_only=True,      # Only books with inventory
    page=1,                  # Page number
    per_page=20              # Items per page
)
# results is a dict with:
# {
#     'items': [Book, Book, ...],  # List of books
#     'total': 42,                 # Total matching books
#     'page': 1,                   # Current page
#     'pages': 3,                  # Total pages
#     'per_page': 20               # Items per page
# }

# READ - Get books by author
books = book_service.get_by_author("Robert Martin")

# READ - Get books by category
books = book_service.get_by_category("Programming")

# READ - Get all categories
categories = book_service.get_categories()
# Returns: ['Fiction', 'Programming', 'Science', ...]

# UPDATE a book
book = book_service.update_book(
    book_id=UUID("your-book-id"),
    title="Updated Title",      # Optional
    author="Updated Author",    # Optional
    isbn="978-0-00-000000-0",  # Optional
    publisher="New Publisher",  # Optional
    year_published=2024,        # Optional
    description="New desc",     # Optional
    category="New Category",    # Optional
    auto_commit=True
)

# DELETE (soft delete - marks as inactive)
book = book_service.deactivate_book(book_id=UUID("your-book-id"))

# RESTORE (reactivate a deactivated book)
book = book_service.reactivate_book(book_id=UUID("your-book-id"))
```

#### InventoryService Methods

```python
from app.api import get_inventory_service
from decimal import Decimal
from uuid import UUID

inventory_service = get_inventory_service()

# ADD inventory (or update if same book/warehouse/condition exists)
inventory = inventory_service.add_inventory(
    book_id=UUID("book-id"),
    warehouse_id=UUID("warehouse-id"),
    condition=4,                        # 1=Poor, 2=Fair, 3=Good, 4=Very Good, 5=Fine
    quantity=10,                        # Number of copies
    acquisition_cost=Decimal("15.00"),  # What we paid
    list_price=Decimal("29.99"),        # What we sell for
    reorder_level=2,                    # Alert when stock drops to this
    location_code="A1-S3",              # Shelf location
    auto_commit=True
)

# GET inventory by book
items = inventory_service.get_by_book(
    book_id=UUID("book-id"),
    in_stock_only=True  # Only items with quantity > 0
)

# GET low stock items
low_stock = inventory_service.get_low_stock(
    warehouse_id=UUID("warehouse-id")  # Optional filter
)

# ADJUST quantity (add or remove)
inventory = inventory_service.adjust_quantity(
    inventory_id=UUID("inventory-id"),
    delta=5,      # Positive to add, negative to remove
    reason="Received shipment",  # Optional audit note
    auto_commit=True
)

# RESERVE for a sale (reduces quantity)
inventory = inventory_service.reserve_inventory(
    inventory_id=UUID("inventory-id"),
    quantity=2,
    auto_commit=True
)

# GET total inventory value
value = inventory_service.get_total_value(
    warehouse_id=UUID("warehouse-id")  # Optional
)
# Returns: {'acquisition_value': Decimal('1500.00'), 'list_value': Decimal('2999.00')}

# CREATE a warehouse
warehouse = inventory_service.create_warehouse(
    name="Main Warehouse",
    location="123 Storage Lane",
    capacity=10000,
    auto_commit=True
)

# GET all warehouses
warehouses = inventory_service.get_warehouses()
```

#### InvoiceService Methods

```python
from app.api import get_invoice_service
from uuid import UUID

invoice_service = get_invoice_service()

# CREATE a new invoice
invoice = invoice_service.create_invoice(
    customer_id=UUID("customer-id"),
    created_by=UUID("user-id"),       # The employee creating it
    payment_terms="Net 30",
    notes="Special handling required",
    auto_commit=True
)
# Invoice is created with status='draft'

# ADD inventory item to invoice
line = invoice_service.add_inventory_line(
    invoice_id=UUID("invoice-id"),
    inventory_id=UUID("inventory-id"),
    quantity=1,
    auto_commit=True
)

# ADD pending book request to invoice
line = invoice_service.add_request_line(
    invoice_id=UUID("invoice-id"),
    request_id=UUID("book-request-id"),
    auto_commit=True
)

# ADD custom line (e.g., shipping)
line = invoice_service.add_custom_line(
    invoice_id=UUID("invoice-id"),
    description="Shipping and Handling",
    quantity=1,
    unit_price=Decimal("15.00"),
    auto_commit=True
)

# REMOVE a line
success = invoice_service.remove_line(
    line_id=UUID("line-id"),
    auto_commit=True
)

# SEND invoice (changes status from 'draft' to 'sent')
invoice = invoice_service.send_invoice(
    invoice_id=UUID("invoice-id"),
    auto_commit=True
)

# MARK as paid (changes status from 'sent' to 'paid')
invoice = invoice_service.mark_paid(
    invoice_id=UUID("invoice-id"),
    auto_commit=True
)

# CANCEL invoice
invoice = invoice_service.cancel_invoice(
    invoice_id=UUID("invoice-id"),
    auto_commit=True
)

# GET invoice by number
invoice = invoice_service.get_by_number("INV-20260101-0001")

# GET customer's invoices
results = invoice_service.get_by_customer(
    customer_id=UUID("customer-id"),
    status="sent",  # Optional filter
    page=1,
    per_page=20
)

# GET overdue invoices (sent but not paid after X days)
overdue = invoice_service.get_overdue(payment_days=30)
```

---

## 6. Working with Repositories

Repositories provide **direct database access**. Use them when you need more control than services provide.

### When to Use Repositories vs Services

| Use Services When... | Use Repositories When... |
|---------------------|-------------------------|
| You need business logic | You need raw database queries |
| You want automatic validation | You're building custom reports |
| You want error handling | You need maximum performance |
| You're building normal features | You're doing bulk operations |

### Repository Example

```python
from app.repositories import BookRepository

book_repo = BookRepository()

# Basic CRUD operations
book = book_repo.get_by_id(UUID("book-id"))        # Get one by ID
books = book_repo.get_all(page=1, per_page=20)     # Get all (paginated)
books = book_repo.find_by(category="Fiction")      # Find by field
exists = book_repo.exists(isbn="978-0-13-235088-4") # Check if exists
count = book_repo.count(category="Fiction")        # Count matching

# Create (returns model, doesn't commit)
book = book_repo.create(
    title="New Book",
    author="Author Name"
)
book_repo.commit()  # Save to database

# Update
book = book_repo.update(book, title="Updated Title")
book_repo.commit()

# Delete
book_repo.delete(book)
book_repo.commit()

# Soft delete (sets is_active=False)
book_repo.soft_delete(book)
book_repo.commit()
```

---

## 7. Working with Schemas (DTOs)

Schemas define the **shape of data** that goes in and out of the API.

### Why Use Schemas?

1. **Security**: Never expose sensitive fields (like passwords)
2. **Validation**: Catch bad data before it reaches the database
3. **Documentation**: Clear contract of what data is expected
4. **Flexibility**: Change internal models without breaking external APIs

### Using Schemas

#### Converting Model to Schema (for API responses)

```python
from app.models import Book
from app.schemas import BookSchema

# Get a book from the database
book = Book.query.first()

# Convert to schema
book_schema = BookSchema.from_model(book, include_inventory_stats=True)

# Convert to dictionary (for JSON response)
book_dict = book_schema.to_dict()

# book_dict now looks like:
# {
#     'id': 'uuid-string',
#     'title': 'Clean Code',
#     'author': 'Robert Martin',
#     'isbn': '978-0-13-235088-4',
#     'total_quantity': 15,
#     'lowest_price': 29.99,
#     'in_stock': True,
#     ...
# }
```

#### Validating Input Data

```python
from app.schemas import BookCreateSchema

# Data from user request
user_data = {
    'title': 'New Book',
    'author': 'Some Author',
    'isbn': 'invalid-isbn'  # Bad data!
}

# Create schema from input
schema = BookCreateSchema.from_dict(user_data)

# Validate
errors = schema.validate()

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"  - {error}")
    # Output:
    # Validation failed:
    #   - ISBN: Invalid ISBN-10 format
else:
    # Data is valid, proceed
    book_service.create_book(**user_data)
```

### Available Schemas

| Schema | Purpose |
|--------|---------|
| `UserSchema` | User data for responses |
| `UserCreateSchema` | Data for creating users |
| `UserUpdateSchema` | Data for updating users |
| `CustomerSchema` | Customer data for responses |
| `CustomerCreateSchema` | Data for customer registration |
| `AddressSchema` | Address data |
| `BookSchema` | Book data for responses |
| `BookCreateSchema` | Data for creating books |
| `BookUpdateSchema` | Data for updating books |
| `InventorySchema` | Inventory data for responses |
| `InventoryCreateSchema` | Data for adding inventory |
| `InvoiceSchema` | Invoice data for responses |
| `InvoiceLineSchema` | Invoice line item data |
| `BookRequestSchema` | Book request data |
| `PurchaseOrderSchema` | Purchase order data |
| `POLineSchema` | PO line item data |

---

## 8. Working with Models

Models represent **database tables** as Python classes.

### Understanding Models

```python
from app.models import Book

# A Model is a Python class that represents a database table
# Each instance of the class represents one row in the table

# The Book model represents the 'books' table
# It has these fields (columns):
book = Book(
    isbn="978-0-13-235088-4",     # Optional, can be None
    title="Clean Code",            # Required
    author="Robert Martin",        # Required
    publisher="Prentice Hall",     # Optional
    year_published=2008,           # Optional
    description="A handbook...",   # Optional
    category="Programming",        # Optional
    is_active=True                 # Default: True
)

# The model also has these automatic fields:
# - id: UUID primary key (auto-generated)
# - created_at: Timestamp when created
# - updated_at: Timestamp when last modified
```

### Model Relationships

Models can be related to each other:

```python
from app.models import Customer, Invoice

# A Customer HAS MANY Invoices
customer = Customer.query.first()
invoices = customer.invoices  # List of Invoice objects

# An Invoice BELONGS TO a Customer
invoice = Invoice.query.first()
customer = invoice.customer  # The Customer object
```

### Model Methods

Models have helpful methods:

```python
from app.models import Inventory

# Get inventory item
inventory = Inventory.query.first()

# Use model methods
print(inventory.condition_label)  # "Very Good" instead of 4
print(inventory.is_low_stock)     # True/False
print(inventory.profit_margin)    # Percentage as float

# Adjust quantity
inventory.adjust_quantity(5)   # Add 5
inventory.adjust_quantity(-3)  # Remove 3

# Convert to dictionary
data = inventory.to_dict()
```

---

## 9. Complete Code Examples

### Example 1: Adding a New Book with Inventory

This example shows the complete flow of adding a book and some inventory.

```python
"""
Complete Example: Adding a Book with Inventory
==============================================

This script demonstrates:
1. Creating a new book in the catalog
2. Creating a warehouse (if needed)
3. Adding inventory for that book
4. Searching for the book
"""

from decimal import Decimal
from app.api import get_book_service, get_inventory_service

def add_book_with_inventory():
    """Add a new book and some inventory."""
    
    # Step 1: Get the services
    book_service = get_book_service()
    inventory_service = get_inventory_service()
    
    # Step 2: Create the book
    print("Creating book...")
    try:
        book = book_service.create_book(
            title="Design Patterns",
            author="Gang of Four",
            isbn="978-0-201-63361-0",
            publisher="Addison-Wesley",
            year_published=1994,
            category="Programming",
            description="Elements of Reusable Object-Oriented Software"
        )
        print(f"✓ Created book: {book.title} (ID: {book.id})")
    except Exception as e:
        print(f"✗ Failed to create book: {e}")
        return
    
    # Step 3: Get or create a warehouse
    print("\nGetting warehouse...")
    warehouses = inventory_service.get_warehouses()
    
    if warehouses:
        warehouse = warehouses[0]
        print(f"✓ Using existing warehouse: {warehouse.name}")
    else:
        warehouse = inventory_service.create_warehouse(
            name="Main Warehouse",
            location="123 Storage Lane",
            capacity=10000
        )
        print(f"✓ Created warehouse: {warehouse.name}")
    
    # Step 4: Add inventory
    print("\nAdding inventory...")
    
    # Add 5 copies in "Very Good" condition
    inventory_vg = inventory_service.add_inventory(
        book_id=book.id,
        warehouse_id=warehouse.id,
        condition=4,  # Very Good
        quantity=5,
        acquisition_cost=Decimal("25.00"),
        list_price=Decimal("49.99"),
        reorder_level=2,
        location_code="A1-S5"
    )
    print(f"✓ Added {inventory_vg.quantity} copies ({inventory_vg.condition_label}) @ ${inventory_vg.list_price}")
    
    # Add 3 copies in "Good" condition
    inventory_g = inventory_service.add_inventory(
        book_id=book.id,
        warehouse_id=warehouse.id,
        condition=3,  # Good
        quantity=3,
        acquisition_cost=Decimal("15.00"),
        list_price=Decimal("35.99"),
        reorder_level=1,
        location_code="A1-S6"
    )
    print(f"✓ Added {inventory_g.quantity} copies ({inventory_g.condition_label}) @ ${inventory_g.list_price}")
    
    # Step 5: Verify by searching
    print("\nVerifying...")
    results = book_service.search(query="Design Patterns", in_stock_only=True)
    
    if results['items']:
        found_book = results['items'][0]
        print(f"✓ Found book: {found_book.title}")
        print(f"  Total quantity: {found_book.get_total_quantity()}")
        print(f"  Lowest price: ${found_book.get_lowest_price()}")
        print(f"  Available conditions: {found_book.get_available_conditions()}")
    else:
        print("✗ Book not found in search!")
    
    print("\nDone!")
    return book


# Run the example
if __name__ == "__main__":
    # Make sure we're in application context
    from app import create_app
    app = create_app('development')
    
    with app.app_context():
        add_book_with_inventory()
```

### Example 2: Creating a Customer and Invoice

```python
"""
Complete Example: Customer Registration and Invoice Creation
============================================================

This script demonstrates:
1. Creating a new customer account
2. Adding an address
3. Creating an invoice
4. Adding line items
5. Sending the invoice
"""

from decimal import Decimal
from uuid import UUID
from app.api import (
    get_customer_service,
    get_invoice_service,
    get_inventory_service,
    get_user_service
)

def create_customer_and_invoice():
    """Create a customer, then create an invoice for them."""
    
    # Get services
    customer_service = get_customer_service()
    invoice_service = get_invoice_service()
    inventory_service = get_inventory_service()
    user_service = get_user_service()
    
    # Step 1: Create a customer account
    print("Creating customer account...")
    try:
        customer = customer_service.create_customer(
            email="john.collector@example.com",
            password="SecurePassword123!",
            first_name="John",
            last_name="Collector",
            company_name="Rare Books Inc.",
            phone="555-0123",
            credit_terms="Net 30"
        )
        print(f"✓ Created customer: {customer.display_name}")
        print(f"  Customer ID: {customer.id}")
        print(f"  User ID: {customer.user_id}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return
    
    # Step 2: Add a billing address
    print("\nAdding address...")
    address = customer_service.add_address(
        customer_id=customer.id,
        street="123 Book Lane",
        city="Library City",
        state="CA",
        zip_code="90210",
        country="USA",
        address_type="billing",
        is_primary=True
    )
    print(f"✓ Added address: {address.city}, {address.state}")
    
    # Step 3: Get an employee to create the invoice
    # (In real code, this would be the logged-in user)
    employees = user_service.get_staff()
    if not employees:
        print("✗ No staff users found! Create one first.")
        return
    employee = employees[0]
    print(f"\nUsing employee: {employee.full_name}")
    
    # Step 4: Find some inventory to sell
    print("\nFinding inventory...")
    inventory_items = []
    
    # Search for available inventory
    results = inventory_service.search(
        query="",  # Empty query = all
        in_stock_only=True,
        page=1,
        per_page=5
    )
    
    if not results['items']:
        print("✗ No inventory found! Add some first.")
        return
    
    inventory_items = results['items'][:2]  # Take first 2 items
    print(f"✓ Found {len(inventory_items)} items to sell")
    
    # Step 5: Create the invoice
    print("\nCreating invoice...")
    invoice = invoice_service.create_invoice(
        customer_id=customer.id,
        created_by=employee.id,
        payment_terms="Net 30",
        notes="Thank you for your business!"
    )
    print(f"✓ Created invoice: {invoice.invoice_number}")
    print(f"  Status: {invoice.status}")
    
    # Step 6: Add line items
    print("\nAdding line items...")
    for inventory in inventory_items:
        line = invoice_service.add_inventory_line(
            invoice_id=invoice.id,
            inventory_id=inventory.id,
            quantity=1
        )
        print(f"  ✓ Added: {line.description}")
        print(f"    Price: ${line.unit_price}")
    
    # Step 7: Check the invoice total
    # Refresh the invoice to get updated subtotal
    invoice = invoice_service.get_by_id(invoice.id)
    print(f"\nInvoice subtotal: ${invoice.subtotal}")
    print(f"Line count: {invoice.line_count}")
    
    # Step 8: Send the invoice
    print("\nSending invoice...")
    invoice = invoice_service.send_invoice(invoice.id)
    print(f"✓ Invoice sent!")
    print(f"  Status: {invoice.status}")
    print(f"  Sent at: {invoice.sent_at}")
    
    # Step 9: Show final invoice
    print("\n" + "="*50)
    print("INVOICE SUMMARY")
    print("="*50)
    print(f"Invoice #: {invoice.invoice_number}")
    print(f"Customer: {invoice.customer.display_name}")
    print(f"Status: {invoice.status}")
    print(f"Payment Terms: {invoice.payment_terms}")
    print(f"Subtotal: ${invoice.subtotal}")
    print("="*50)
    
    return invoice


# Run the example
if __name__ == "__main__":
    from app import create_app
    app = create_app('development')
    
    with app.app_context():
        create_customer_and_invoice()
```

### Example 3: Book Request Workflow

```python
"""
Complete Example: Book Request Workflow
=======================================

This demonstrates the book request feature where:
1. Customer requests a book we don't have
2. When we get the book, we match it to the request
3. Customer is notified and purchases
"""

from decimal import Decimal
from uuid import UUID
from app.api import (
    get_book_request_service,
    get_book_service,
    get_inventory_service,
    get_customer_service
)

def book_request_workflow():
    """Demonstrate the book request workflow."""
    
    # Get services
    request_service = get_book_request_service()
    book_service = get_book_service()
    inventory_service = get_inventory_service()
    customer_service = get_customer_service()
    
    # Step 1: Get a customer (assume one exists)
    print("Getting customer...")
    customers = customer_service.repository.find_by(is_active=True)
    if not customers:
        print("✗ No customers found! Create one first.")
        return
    customer = customers[0]
    print(f"✓ Using customer: {customer.display_name}")
    
    # Step 2: Customer requests a rare book
    print("\nCreating book request...")
    request = request_service.create_request(
        customer_id=customer.id,
        title="Principia Mathematica",
        author="Isaac Newton",
        min_condition=3,  # Good or better
        max_price=Decimal("500.00"),
        notes="First edition preferred",
        expiry_days=365
    )
    print(f"✓ Created request: {request.title}")
    print(f"  Status: {request.status}")
    print(f"  Min condition: {request.min_condition_label}")
    print(f"  Max price: ${request.max_price}")
    print(f"  Expires: {request.expires_at}")
    
    # Step 3: View pending requests (staff perspective)
    print("\nViewing pending requests...")
    pending = request_service.get_pending()
    print(f"✓ Found {pending['total']} pending requests")
    
    # Step 4: Later... we acquire the book!
    print("\n--- TIME PASSES ---")
    print("\nAcquiring the requested book...")
    
    # Create the book entry
    book = book_service.create_book(
        title="Principia Mathematica",
        author="Isaac Newton",
        year_published=1687,
        category="Science",
        description="Mathematical Principles of Natural Philosophy"
    )
    print(f"✓ Created book: {book.title}")
    
    # Add to inventory
    warehouse = inventory_service.get_warehouses()[0]
    inventory = inventory_service.add_inventory(
        book_id=book.id,
        warehouse_id=warehouse.id,
        condition=4,  # Very Good
        quantity=1,
        acquisition_cost=Decimal("350.00"),
        list_price=Decimal("450.00")
    )
    print(f"✓ Added inventory: {inventory.condition_label} @ ${inventory.list_price}")
    
    # Step 5: Check if any requests match this inventory
    print("\nChecking for matching requests...")
    matches = request_service.find_matches_for_inventory(
        book=book,
        condition=inventory.condition,
        price=inventory.list_price
    )
    print(f"✓ Found {len(matches)} matching requests")
    
    # Step 6: Match the request
    if matches:
        matched_request = matches[0]
        print(f"\nMatching request from: {matched_request.customer.display_name}")
        
        request_service.match_request(
            request_id=matched_request.id,
            book_id=book.id,
            inventory_id=inventory.id
        )
        print(f"✓ Request matched!")
        print(f"  Status: {matched_request.status}")
        
        # Step 7: Notify the customer
        print("\nNotifying customer...")
        request_service.notify_customer(matched_request.id)
        print(f"✓ Customer notified!")
        print(f"  Status: {matched_request.status}")
        
        # Step 8: Customer purchases (request fulfilled)
        print("\nCustomer purchases the book...")
        request_service.fulfill_request(matched_request.id)
        print(f"✓ Request fulfilled!")
        print(f"  Final status: {matched_request.status}")
    
    # Step 9: View request statistics
    print("\nRequest statistics:")
    stats = request_service.get_stats()
    for status, count in stats.items():
        print(f"  {status}: {count}")
    
    return request


# Run the example
if __name__ == "__main__":
    from app import create_app
    app = create_app('development')
    
    with app.app_context():
        book_request_workflow()
```

---

## 10. Adding RBAC (Role-Based Access Control)

**NOTE**: RBAC implementation is assigned to another team member. This section shows how to integrate RBAC with the existing codebase.

### The Hook System

We've created a "hook" system that allows RBAC to be added without modifying services.

```python
# In app/api/hooks.py, there are hook points for:
# - Permission checking
# - Audit logging
# - Cross-module events
```

### How to Add Permission Checking

The RBAC team should implement these steps:

#### Step 1: Create Permission Checker

```python
# In your RBAC module (e.g., app/rbac/permissions.py)

def check_user_permission(user, permission: str) -> bool:
    """
    Check if user has the specified permission.
    
    Args:
        user: The current user object (or None if not logged in)
        permission: The permission name to check
        
    Returns:
        True if user has permission, False otherwise
    """
    if user is None:
        return False
    
    # Your permission logic here
    # Example using a simple role-based check:
    
    ROLE_PERMISSIONS = {
        'admin': ['*'],  # Admin can do everything
        'employee': [
            'view_inventory',
            'manage_inventory',
            'view_books',
            'manage_books',
            'view_invoices',
            'create_invoices',
            'view_customers',
        ],
        'customer': [
            'view_own_profile',
            'view_catalog',
            'create_request',
            'view_own_invoices',
        ]
    }
    
    user_permissions = ROLE_PERMISSIONS.get(user.role, [])
    
    # Admin wildcard
    if '*' in user_permissions:
        return True
    
    return permission in user_permissions
```

#### Step 2: Register the Hook

```python
# In your app initialization (e.g., app/__init__.py)

from app.api.hooks import register_permission_hook
from app.rbac.permissions import check_user_permission

# Register the permission hook
register_permission_hook(check_user_permission)
```

#### Step 3: Use Permission Decorator

```python
# In your route definitions

from app.api.hooks import require_permission

@app.route('/api/inventory', methods=['POST'])
@require_permission('manage_inventory')
def add_inventory():
    """Add inventory - requires manage_inventory permission."""
    # Your code here
    pass
```

### Available Hook Functions

```python
from app.api.hooks import (
    # Registration functions
    register_permission_hook,    # Register permission checker
    register_audit_hook,         # Register audit logger
    register_event_hook,         # Register event handler
    
    # Usage functions
    check_permission,            # Check a permission
    audit,                       # Log an audit event
    emit_event,                  # Emit an event
    
    # Decorators
    require_permission,          # Decorator for routes
    
    # Event constants
    EVENT_INVENTORY_ADDED,
    EVENT_INVOICE_SENT,
    EVENT_REQUEST_MATCHED,
    # ... etc
)
```

### Permission Names to Implement

Here are the permission names used throughout the system:

| Permission | Description | Used By |
|------------|-------------|---------|
| `manage_users` | Create, update, deactivate users | UserService |
| `view_users` | View user list | UserService |
| `manage_inventory` | Add, update inventory | InventoryService |
| `delete_inventory` | Remove inventory items | InventoryService |
| `view_inventory` | View inventory levels | InventoryService |
| `manage_books` | Add, update books | BookService |
| `delete_books` | Deactivate books | BookService |
| `view_books` | View book catalog | BookService |
| `manage_invoices` | Create, modify invoices | InvoiceService |
| `delete_invoices` | Cancel invoices | InvoiceService |
| `view_invoices` | View all invoices | InvoiceService |
| `view_own_invoices` | View own invoices | InvoiceService |
| `manage_requests` | Process book requests | BookRequestService |
| `create_request` | Create book request | BookRequestService |
| `manage_purchase_orders` | Create, submit POs | PurchaseOrderService |
| `receive_purchase_orders` | Receive PO shipments | PurchaseOrderService |

---

## 11. Error Handling

### Types of Errors

The service layer raises specific exceptions you should catch:

```python
from app.services.base import (
    ServiceError,      # Base error class
    ValidationError,   # Input validation failed
    NotFoundError,     # Resource not found
    ConflictError,     # Operation conflicts with current state
)
```

### Handling Errors in Your Code

```python
from app.api import get_book_service
from app.services.base import ValidationError, NotFoundError, ConflictError

book_service = get_book_service()

try:
    book = book_service.create_book(
        title="",  # Empty title - will fail validation
        author="Someone"
    )
except ValidationError as e:
    # e.errors is a list of error messages
    print(f"Validation failed: {e.errors}")
    # Output: Validation failed: ['Title is required']
    
except ConflictError as e:
    # e.message explains the conflict
    print(f"Conflict: {e.message}")
    # Output: Conflict: A book with this ISBN already exists
    
except NotFoundError as e:
    # e.message explains what wasn't found
    print(f"Not found: {e.message}")
    # Output: Not found: Book not found: uuid-here
    
except Exception as e:
    # Catch-all for unexpected errors
    print(f"Unexpected error: {e}")
```

### Error Response Helpers

For API endpoints, use the response helpers:

```python
from app.api import api_success, api_error, api_validation_error, api_not_found

# Success response
return api_success(
    data={'book_id': str(book.id)},
    message="Book created successfully"
)
# Returns: ({'success': True, 'data': {...}, 'message': '...'}, 200)

# Validation error
return api_validation_error(['Title is required', 'Author is required'])
# Returns: ({'success': False, 'error': {...}}, 400)

# Not found error
return api_not_found('Book', book_id)
# Returns: ({'success': False, 'error': {...}}, 404)

# Generic error
return api_error(
    message="Something went wrong",
    code="INTERNAL_ERROR",
    status=500
)
```

---

## 12. Testing Your Code

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run specific test class
pytest tests/test_models.py::TestBookModel

# Run specific test method
pytest tests/test_models.py::TestBookModel::test_create_book

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Writing Tests

```python
# tests/test_my_feature.py

import pytest
from decimal import Decimal

class TestMyFeature:
    """Tests for my new feature."""
    
    def test_basic_functionality(self, book_service, session):
        """Test that basic feature works."""
        # Arrange - set up test data
        book = book_service.create_book(
            title="Test Book",
            author="Test Author",
            auto_commit=False  # Don't commit - test isolation
        )
        
        # Act - perform the action
        result = book_service.get_by_id(book.id)
        
        # Assert - verify the result
        assert result is not None
        assert result.title == "Test Book"
    
    def test_validation_error(self, book_service, session):
        """Test that validation errors are raised."""
        from app.services.base import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            book_service.create_book(
                title="",  # Invalid - empty
                author="Author",
                auto_commit=False
            )
        
        assert "Title" in str(exc_info.value.errors)
    
    def test_with_fixtures(self, book_service, sample_book, warehouse, session):
        """Test using fixtures from conftest.py."""
        # sample_book is already created by the fixture
        result = book_service.get_by_id(sample_book.id)
        assert result.title == sample_book.title
```

### Available Test Fixtures

These are defined in `tests/conftest.py`:

| Fixture | Description |
|---------|-------------|
| `app` | Flask application instance |
| `db` | Database instance |
| `session` | Isolated database session |
| `client` | Test HTTP client |
| `admin_user` | Admin user account |
| `employee_user` | Employee user account |
| `customer_user` | Customer user account |
| `customer` | Customer with profile |
| `customer_address` | Customer address |
| `sample_book` | Example book |
| `multiple_books` | List of books |
| `warehouse` | Warehouse |
| `inventory` | Inventory item |
| `invoice` | Draft invoice |
| `book_request` | Book request |
| `manufacturer` | Manufacturer |
| `purchase_order` | Purchase order |
| `user_service` | UserService instance |
| `book_service` | BookService instance |
| ... | (all services available) |

---

## 13. Common Mistakes and How to Avoid Them

### Mistake 1: Forgetting Application Context

**Problem**: Flask requires an "application context" to access the database.

```python
# THIS WILL FAIL
from app.models import Book
books = Book.query.all()  # Error: No application context!
```

**Solution**: Always use application context.

```python
# Option 1: In Flask routes (automatic)
@app.route('/books')
def list_books():
    books = Book.query.all()  # Works! Flask provides context
    return render_template('books.html', books=books)

# Option 2: In scripts
from app import create_app
app = create_app()

with app.app_context():
    books = Book.query.all()  # Works! We provided context

# Option 3: Using Flask shell
# $ flask shell
# >>> from app.models import Book
# >>> books = Book.query.all()  # Works! Shell provides context
```

### Mistake 2: Not Committing Transactions

**Problem**: Changes aren't saved to the database.

```python
# THIS WON'T SAVE
from app.models import Book
from app.extensions import db

book = Book(title="New Book", author="Author")
db.session.add(book)
# Forgot to commit!
```

**Solution**: Always commit (or use auto_commit=True).

```python
# Option 1: Manual commit
book = Book(title="New Book", author="Author")
db.session.add(book)
db.session.commit()  # Now it's saved!

# Option 2: Use services with auto_commit=True (default)
book_service = BookService()
book = book_service.create_book(
    title="New Book",
    author="Author"
)  # Automatically committed!
```

### Mistake 3: Mixing Layers

**Problem**: Putting database code in route handlers.

```python
# BAD - database code in route
@app.route('/books/search')
def search_books():
    query = request.args.get('q')
    books = Book.query.filter(Book.title.ilike(f'%{query}%')).all()
    return jsonify([b.to_dict() for b in books])
```

**Solution**: Use services.

```python
# GOOD - use service
@app.route('/books/search')
def search_books():
    query = request.args.get('q')
    book_service = get_book_service()
    results = book_service.search(query)
    return jsonify({
        'books': [BookSchema.from_model(b).to_dict() for b in results['items']],
        'total': results['total']
    })
```

### Mistake 4: Not Handling Errors

**Problem**: Exceptions crash the application.

```python
# BAD - no error handling
@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    book_service = get_book_service()
    book_service.deactivate_book(UUID(book_id))  # What if not found?
    return jsonify({'success': True})
```

**Solution**: Catch and handle exceptions.

```python
# GOOD - with error handling
from app.services.base import NotFoundError

@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        book_service = get_book_service()
        book_service.deactivate_book(UUID(book_id))
        return api_success(message="Book deactivated")
    except NotFoundError:
        return api_not_found('Book', book_id)
    except Exception as e:
        return api_error(str(e), status=500)
```

### Mistake 5: Exposing Sensitive Data

**Problem**: Returning models directly exposes all fields.

```python
# BAD - exposes password_hash!
@app.route('/users/<user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    return jsonify(user.to_dict())  # Includes password_hash!
```

**Solution**: Use schemas.

```python
# GOOD - schema excludes sensitive fields
@app.route('/users/<user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    return jsonify(UserSchema.from_model(user).to_dict())
```

### Mistake 6: UUID String vs UUID Object

**Problem**: Confusing UUID strings with UUID objects.

```python
# THIS WILL FAIL
book_id = "12345678-1234-1234-1234-123456789012"  # String!
book = book_service.get_by_id(book_id)  # Might not work
```

**Solution**: Convert strings to UUID objects.

```python
from uuid import UUID

book_id_string = "12345678-1234-1234-1234-123456789012"
book_id = UUID(book_id_string)  # Now it's a UUID object
book = book_service.get_by_id(book_id)  # Works!
```

---

## 14. Glossary of Terms

| Term | Definition |
|------|------------|
| **API** | Application Programming Interface - a way for code to communicate |
| **CRUD** | Create, Read, Update, Delete - the basic database operations |
| **DTO** | Data Transfer Object - a class that carries data between layers |
| **Factory** | A function that creates and returns objects |
| **Flask** | A Python web framework |
| **Model** | A Python class representing a database table |
| **ORM** | Object-Relational Mapping - converts database rows to objects |
| **RBAC** | Role-Based Access Control - limiting what users can do based on their role |
| **Repository** | A class that handles database operations for one entity |
| **Schema** | A class defining the structure of data |
| **Service** | A class containing business logic |
| **SQLAlchemy** | A Python library for working with databases |
| **UUID** | Universally Unique Identifier - a unique ID format |
| **Validation** | Checking that input data is correct |

---

## Quick Reference Card

### Import Statements

```python
# Services
from app.services import (
    UserService, CustomerService, BookService,
    InventoryService, InvoiceService, BookRequestService,
    PurchaseOrderService
)

# Service factories (recommended)
from app.api import (
    get_user_service, get_customer_service, get_book_service,
    get_inventory_service, get_invoice_service, get_book_request_service,
    get_purchase_order_service
)

# Schemas
from app.schemas import (
    UserSchema, CustomerSchema, BookSchema, InventorySchema,
    InvoiceSchema, BookRequestSchema, PurchaseOrderSchema
)

# Models
from app.models import (
    User, Customer, Address, Book, Warehouse, Inventory,
    Invoice, InvoiceLine, BookRequest, Manufacturer,
    PurchaseOrder, POLine
)

# Errors
from app.services.base import (
    ServiceError, ValidationError, NotFoundError, ConflictError
)

# Response helpers
from app.api import (
    api_success, api_error, api_validation_error, api_not_found
)

# Hooks (for RBAC integration)
from app.api.hooks import (
    register_permission_hook, require_permission,
    check_permission, audit, emit_event
)
```

### Common Patterns

```python
# Get service, use service, handle errors
from app.api import get_book_service, api_success, api_error
from app.services.base import ValidationError, NotFoundError

def my_function():
    try:
        service = get_book_service()
        result = service.some_method(...)
        return api_success(data=result.to_dict())
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('Resource', id)
    except Exception as e:
        return api_error(str(e), status=500)
```

---

## Need Help?

1. Check this documentation first
2. Look at the test files for examples
3. Use Flask shell to experiment: `flask shell`
4. Check the error messages - they're designed to be helpful!

Happy coding! 🎉
