# Testing & Quality Assurance

**Related Stories:** US-009, US-010  
**Related Tasks:** S2-13 (Integration testing setup)

---

## 1. Overview

Testing strategy ensures all Definition of Done criteria are met through:
- Unit tests for individual functions
- Integration tests for module interactions
- End-to-end tests for user workflows
- Security testing for access control
- Performance testing for response times

---

## 2. Definition of Done Reference

From the project DoD (Section 4 - Testing & QA):
> - Every function shall have test cases for success, failure, edge cases
> - Tests from Admin and Customer perspectives
> - Integration between modules tested
> - Security penetration testing performed

From Code Quality Standards:
> - Unit tests pass
> - Peer review completed
> - Documentation updated

---

## 3. Testing Pyramid

```
                    ┌─────────────┐
                    │    E2E      │  ← Few, slow, high confidence
                    │   Tests     │
                    ├─────────────┤
                    │ Integration │  ← Module interactions
                    │    Tests    │
               ┌────┴─────────────┴────┐
               │      Unit Tests       │  ← Many, fast, isolated
               └───────────────────────┘
```

| Level | Count Target | Execution Time | Tools |
|-------|--------------|----------------|-------|
| Unit | 70% of tests | < 1 sec each | pytest |
| Integration | 20% of tests | < 5 sec each | pytest + TestClient |
| E2E | 10% of tests | < 30 sec each | Playwright/Cypress |

---

## 4. Test Categories by Module

### 4.1 Authentication Tests

| Test ID | Description | Type | Priority |
|---------|-------------|------|----------|
| AUTH-001 | Valid login returns JWT | Unit | High |
| AUTH-002 | Invalid password rejected | Unit | High |
| AUTH-003 | Expired token rejected | Unit | High |
| AUTH-004 | Role-based access enforced | Integration | High |
| AUTH-005 | Password hashing secure | Unit | High |
| AUTH-006 | Registration validates email | Unit | Medium |
| AUTH-007 | Brute-force protection | Security | High |

### 4.2 Inventory Tests

| Test ID | Description | Type | Priority |
|---------|-------------|------|----------|
| INV-001 | Search returns correct results | Integration | High |
| INV-002 | Pagination works correctly | Unit | Medium |
| INV-003 | Stock counts accurate | Integration | High |
| INV-004 | Incoming quantity calculated | Integration | Medium |
| INV-005 | Low-stock status correct | Unit | High |
| INV-006 | Admin/Employee access only | Security | High |
| INV-007 | Search < 1 second | Performance | Medium |
| INV-008 | ISBN validation works | Unit | Medium |

### 4.3 Sales Tests

| Test ID | Description | Type | Priority |
|---------|-------------|------|----------|
| SALE-001 | Transaction created correctly | Integration | High |
| SALE-002 | Inventory decremented atomically | Integration | Critical |
| SALE-003 | Insufficient stock rejected | Unit | High |
| SALE-004 | Tax calculation correct | Unit | High |
| SALE-005 | Search filters work | Integration | Medium |
| SALE-006 | Daily report accurate | Integration | Medium |
| SALE-007 | Transaction rollback on error | Integration | Critical |

### 4.4 Purchase Order Tests

| Test ID | Description | Type | Priority |
|---------|-------------|------|----------|
| PO-001 | Draft PO created | Integration | High |
| PO-002 | Submit changes status | Unit | High |
| PO-003 | Receive updates inventory | Integration | Critical |
| PO-004 | Partial receive supported | Integration | Medium |
| PO-005 | Cannot edit submitted PO | Unit | High |
| PO-006 | Admin-only submit | Security | High |
| PO-007 | PDF generation complete | Unit | Low |

### 4.5 Customer Portal Tests

| Test ID | Description | Type | Priority |
|---------|-------------|------|----------|
| CUST-001 | Browse without login | Integration | High |
| CUST-002 | Add to cart as guest | Integration | High |
| CUST-003 | Cart merges on login | Integration | Medium |
| CUST-004 | Checkout reserves inventory | Integration | Critical |
| CUST-005 | Confirmation email sent | Integration | High |
| CUST-006 | Order history accurate | Integration | Medium |
| CUST-007 | Out-of-stock blocked | Unit | High |
| CUST-008 | Payment failure rollback | Integration | Critical |

---

## 5. Test Implementation

### 5.1 Project Structure

```
backend/
├── tests/
│   ├── conftest.py          # Fixtures
│   ├── unit/
│   │   ├── test_auth.py
│   │   ├── test_inventory.py
│   │   ├── test_sales.py
│   │   └── test_orders.py
│   ├── integration/
│   │   ├── test_auth_flow.py
│   │   ├── test_sale_process.py
│   │   ├── test_po_lifecycle.py
│   │   └── test_checkout.py
│   ├── e2e/
│   │   ├── test_admin_workflows.py
│   │   └── test_customer_journey.py
│   └── security/
│       ├── test_authorization.py
│       └── test_input_validation.py
```

### 5.2 Fixtures (conftest.py)

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from app.core.database import Base, get_db

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost/test_bookstore",
        echo=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(test_engine):
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def admin_token(client):
    response = await client.post("/auth/login", json={
        "email": "admin@test.com",
        "password": "testpass123"
    })
    return response.json()["access_token"]

@pytest.fixture
async def sample_book(db_session):
    book = Book(
        isbn="978-0-13-235088-4",
        title="Clean Code",
        author="Robert C. Martin",
        mfr_price=Decimal("35.00"),
        list_price=Decimal("49.99")
    )
    db_session.add(book)
    await db_session.commit()
    return book
```

### 5.3 Unit Test Example

```python
# tests/unit/test_inventory.py

import pytest
from decimal import Decimal
from app.services.inventory_service import InventoryService
from app.schemas.inventory import StockStatus

class TestStockStatusCalculation:
    def test_in_stock_when_quantity_above_reorder(self):
        status = InventoryService.calculate_status(
            quantity=50, reorder_level=10
        )
        assert status == StockStatus.IN_STOCK
    
    def test_low_stock_when_at_reorder_level(self):
        status = InventoryService.calculate_status(
            quantity=10, reorder_level=10
        )
        assert status == StockStatus.LOW_STOCK
    
    def test_low_stock_when_below_reorder(self):
        status = InventoryService.calculate_status(
            quantity=5, reorder_level=10
        )
        assert status == StockStatus.LOW_STOCK
    
    def test_out_of_stock_when_zero(self):
        status = InventoryService.calculate_status(
            quantity=0, reorder_level=10
        )
        assert status == StockStatus.OUT_OF_STOCK

class TestISBNValidation:
    @pytest.mark.parametrize("isbn,expected", [
        ("978-0-13-235088-4", True),
        ("0-13-235088-1", True),
        ("invalid", False),
        ("978-0-13-235088-X", False),
        ("", False),
    ])
    def test_isbn_validation(self, isbn, expected):
        result = InventoryService.validate_isbn(isbn)
        assert result == expected
```

### 5.4 Integration Test Example

```python
# tests/integration/test_sale_process.py

import pytest
from decimal import Decimal

class TestSaleProcess:
    @pytest.mark.asyncio
    async def test_process_sale_creates_transaction(
        self, client, admin_token, sample_book, db_session
    ):
        # Setup inventory
        inventory = Inventory(
            book_id=sample_book.id,
            warehouse_id=MAIN_WAREHOUSE_ID,
            quantity=10
        )
        db_session.add(inventory)
        await db_session.commit()
        
        # Process sale
        response = await client.post(
            "/api/sales",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "line_items": [{
                    "book_id": str(sample_book.id),
                    "quantity": 2,
                    "unit_price": "49.99"
                }],
                "payment_method": "card"
            }
        )
        
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["subtotal"] == "99.98"
        assert "transaction_number" in data
        
        # Verify inventory decremented
        await db_session.refresh(inventory)
        assert inventory.quantity == 8
    
    @pytest.mark.asyncio
    async def test_sale_fails_insufficient_stock(
        self, client, admin_token, sample_book, db_session
    ):
        # Setup low inventory
        inventory = Inventory(
            book_id=sample_book.id,
            warehouse_id=MAIN_WAREHOUSE_ID,
            quantity=1
        )
        db_session.add(inventory)
        await db_session.commit()
        
        response = await client.post(
            "/api/sales",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "line_items": [{
                    "book_id": str(sample_book.id),
                    "quantity": 5,
                    "unit_price": "49.99"
                }],
                "payment_method": "card"
            }
        )
        
        assert response.status_code == 422
        assert "insufficient stock" in response.json()["error"]["message"].lower()
        
        # Verify inventory unchanged
        await db_session.refresh(inventory)
        assert inventory.quantity == 1  # Rollback worked
```

### 5.5 Security Test Example

```python
# tests/security/test_authorization.py

import pytest

class TestRoleBasedAccess:
    @pytest.mark.asyncio
    async def test_employee_cannot_delete_book(
        self, client, employee_token, sample_book
    ):
        response = await client.delete(
            f"/api/inventory/{sample_book.id}",
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_customer_cannot_access_sales(
        self, client, customer_token
    ):
        response = await client.get(
            "/api/sales",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_no_token_rejected(self, client):
        response = await client.get("/api/inventory")
        assert response.status_code == 401
```

---

## 6. CI/CD Integration (S1-8)

### 6.1 GitHub Actions Workflow

```yaml
# .github/workflows/test.yml

name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_bookstore
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r backend/requirements-dev.txt
      
      - name: Run linting
        run: |
          cd backend
          flake8 app tests
          black --check app tests
      
      - name: Run tests with coverage
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-fail-under=80
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: backend/coverage.xml
```

---

## 7. Coverage Requirements

| Module | Minimum Coverage | Current |
|--------|------------------|---------|
| Authentication | 90% | - |
| Inventory | 85% | - |
| Sales | 90% | - |
| Purchase Orders | 85% | - |
| Customer Portal | 80% | - |
| **Overall** | **80%** | - |

---

## 8. Performance Testing

### 8.1 Targets (US-010)

| Metric | Target | Test Tool |
|--------|--------|-----------|
| Page load | < 2 seconds | Lighthouse |
| API response | < 500ms (P95) | locust |
| Search latency | < 1 second | pytest-benchmark |
| Concurrent users | 50 minimum | locust |

### 8.2 Load Test Script

```python
# tests/performance/locustfile.py

from locust import HttpUser, task, between

class BookstoreUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
        self.token = response.json()["access_token"]
    
    @task(3)
    def search_inventory(self):
        self.client.get(
            "/api/inventory/search?q=python",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def view_book(self):
        self.client.get(
            f"/api/catalog/{SAMPLE_BOOK_ID}"
        )
    
    @task(1)
    def process_sale(self):
        self.client.post(
            "/api/sales",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "line_items": [{"book_id": SAMPLE_BOOK_ID, "quantity": 1}],
                "payment_method": "card"
            }
        )
```

---

## 9. Test Execution Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific module
pytest tests/unit/test_inventory.py

# Run specific test
pytest tests/unit/test_inventory.py::TestStockStatus::test_low_stock

# Run integration tests only
pytest tests/integration/

# Run with verbose output
pytest -v

# Run performance benchmarks
pytest tests/performance/ --benchmark-only

# Run load tests
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

---

## Next Document: [10-SPRINT-TRACEABILITY.md](10-SPRINT-TRACEABILITY.md)
