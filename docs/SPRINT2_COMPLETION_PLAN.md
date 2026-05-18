# Bookstore Project Completion Plan
## Sprint 2 and Beyond - CS492 Group 4

**Document Version:** 1.0  
**Created:** 2026-05-18  
**Branch:** feature/ui-ux-design

---

## Executive Summary

### Current State Analysis

After reviewing the entire codebase, the project has:

| Component | Status | Completion |
|-----------|--------|------------|
| **Backend Services** | Fully implemented | 95% |
| **Database Models** | Complete | 100% |
| **Repositories** | Complete | 100% |
| **Schemas/DTOs** | Complete | 100% |
| **API Integration Layer** | Service factories + hooks ready | 80% |
| **REST API Endpoints** | **NOT IMPLEMENTED** | 5% |
| **React UI (Frontend)** | UI mockup with mock data | 60% |
| **Frontend-Backend Integration** | **NOT STARTED** | 0% |
| **Authentication/RBAC** | Partial (hooks ready, no implementation) | 30% |
| **Tests** | Unit tests exist | 70% |

### Critical Gap

**The frontend (React/Next.js) and backend (Flask) are completely disconnected.** The UI currently uses hardcoded mock data in `store-context.tsx` and does not call any real API endpoints.

---

## Story ID Numbering System

### New Consistent Format

```
[EPIC]-[SPRINT]-[SEQUENCE]

Examples:
- BE-S2-001 = Backend, Sprint 2, Task 1
- FE-S2-001 = Frontend, Sprint 2, Task 1
- INT-S2-001 = Integration, Sprint 2, Task 1
- QA-S2-001 = QA/Testing, Sprint 2, Task 1
```

### Epic Codes
| Code | Epic |
|------|------|
| BE | Backend API Development |
| FE | Frontend UI Development |
| INT | Frontend-Backend Integration |
| AUTH | Authentication & RBAC |
| QA | Testing & Quality Assurance |
| DOC | Documentation |
| INF | Infrastructure/DevOps |

---

## Mapping: Old Story IDs to New IDs

| Old ID | New ID | Description | Status |
|--------|--------|-------------|--------|
| US-001 | INF-S1-001 | Project Setup and Repository | DONE |
| US-002 | BE-S1-001 | Database Schema Design | DONE |
| US-003 | AUTH-S1-001 | User Auth and Authorization | PARTIAL |
| US-004 | FE-S2-001 | Admin Dashboard Framework | IN PROGRESS |
| US-005 | BE-S2-001 | Inventory Management Module | DONE (services) |
| US-006 | BE-S3-001 | Sales Records Module | DONE (services) |
| US-007 | BE-S3-002 | Purchase Order System | DONE (services) |
| US-008 | FE-S3-001 | Customer Portal Interface | IN PROGRESS |
| US-009 | QA-S4-001 | Integration Testing and QA | PENDING |
| US-010 | QA-S4-002 | Performance and Usability | PENDING |
| US-011 | BE-S4-001 | Data Backup and Integrity | PENDING |
| US-012 | DOC-S4-001 | User/Technical Documentation | PARTIAL |
| S1-1 to S1-21 | Various | Sprint 1 Tasks | See mapping below |
| S2-1 to S2-14 | Various | Sprint 2 Tasks | See mapping below |

---

## Sprint 2 Task Breakdown (Current Sprint)

### CRITICAL PATH: REST API Endpoints

The backend services are complete but have NO REST endpoints. This is the #1 priority.

#### BE-S2-001: Books REST API
**Priority:** P0 (Critical)  
**Est. Hours:** 8  
**Dependencies:** None  
**Owner:** TBD

```
Endpoints to create:
GET    /api/v1/books              - List/search books
GET    /api/v1/books/{id}         - Get book details
POST   /api/v1/books              - Create book
PUT    /api/v1/books/{id}         - Update book
DELETE /api/v1/books/{id}         - Deactivate book
GET    /api/v1/books/categories   - Get all categories
```

**Acceptance Criteria:**
- [ ] All endpoints return proper JSON responses
- [ ] Validation errors return 400 with error details
- [ ] Not found returns 404
- [ ] Pagination works on list endpoint
- [ ] Search by title/author/ISBN works

---

#### BE-S2-002: Inventory REST API
**Priority:** P0 (Critical)  
**Est. Hours:** 10  
**Dependencies:** BE-S2-001  
**Owner:** TBD

```
Endpoints to create:
GET    /api/v1/inventory                    - List inventory
GET    /api/v1/inventory/{id}               - Get inventory item
POST   /api/v1/inventory                    - Add inventory
PUT    /api/v1/inventory/{id}               - Update inventory
PUT    /api/v1/inventory/{id}/adjust        - Adjust quantity
GET    /api/v1/inventory/low-stock          - Get low stock alerts
GET    /api/v1/inventory/value              - Get total inventory value
GET    /api/v1/warehouses                   - List warehouses
POST   /api/v1/warehouses                   - Create warehouse
```

**Acceptance Criteria:**
- [ ] Inventory search works
- [ ] Low stock alerts return correct items
- [ ] Quantity adjustment validates against negative stock
- [ ] Warehouse stats included in response

---

#### BE-S2-003: Invoices/Sales REST API
**Priority:** P1 (High)  
**Est. Hours:** 12  
**Dependencies:** BE-S2-002  
**Owner:** TBD

```
Endpoints to create:
GET    /api/v1/invoices                     - List invoices
GET    /api/v1/invoices/{id}                - Get invoice with lines
POST   /api/v1/invoices                     - Create draft invoice
POST   /api/v1/invoices/{id}/lines          - Add line item
DELETE /api/v1/invoices/{id}/lines/{line}   - Remove line item
POST   /api/v1/invoices/{id}/send           - Send invoice
POST   /api/v1/invoices/{id}/pay            - Mark as paid
POST   /api/v1/invoices/{id}/cancel         - Cancel invoice
GET    /api/v1/invoices/overdue             - Get overdue invoices
GET    /api/v1/invoices/stats               - Get invoice statistics
```

---

#### BE-S2-004: Purchase Orders REST API
**Priority:** P1 (High)  
**Est. Hours:** 10  
**Dependencies:** BE-S2-002  
**Owner:** TBD

```
Endpoints to create:
GET    /api/v1/purchase-orders              - List POs
GET    /api/v1/purchase-orders/{id}         - Get PO with lines
POST   /api/v1/purchase-orders              - Create draft PO
POST   /api/v1/purchase-orders/{id}/lines   - Add line item
DELETE /api/v1/purchase-orders/{id}/lines/{line} - Remove line
POST   /api/v1/purchase-orders/{id}/submit  - Submit PO
POST   /api/v1/purchase-orders/{id}/confirm - Confirm PO
POST   /api/v1/purchase-orders/{id}/receive - Receive shipment
POST   /api/v1/purchase-orders/{id}/cancel  - Cancel PO
GET    /api/v1/manufacturers                - List manufacturers
POST   /api/v1/manufacturers                - Create manufacturer
```

---

#### BE-S2-005: Users/Customers REST API
**Priority:** P1 (High)  
**Est. Hours:** 8  
**Dependencies:** None  
**Owner:** TBD

```
Endpoints to create:
GET    /api/v1/users                        - List users (admin)
GET    /api/v1/users/{id}                   - Get user
POST   /api/v1/users                        - Create user (admin)
PUT    /api/v1/users/{id}                   - Update user
DELETE /api/v1/users/{id}                   - Deactivate user
GET    /api/v1/customers                    - List customers
GET    /api/v1/customers/{id}               - Get customer
POST   /api/v1/customers                    - Register customer
PUT    /api/v1/customers/{id}               - Update customer
GET    /api/v1/customers/{id}/addresses     - Get addresses
POST   /api/v1/customers/{id}/addresses     - Add address
```

---

### Authentication & RBAC

#### AUTH-S2-001: JWT Authentication Implementation
**Priority:** P0 (Critical)  
**Est. Hours:** 12  
**Dependencies:** BE-S2-005  
**Owner:** TBD

```
Tasks:
1. Install flask-jwt-extended
2. Create token generation endpoint (POST /api/v1/auth/login)
3. Create token refresh endpoint (POST /api/v1/auth/refresh)
4. Create logout endpoint (POST /api/v1/auth/logout)
5. Implement @jwt_required decorator on protected routes
6. Add current_user injection to routes
```

**Acceptance Criteria:**
- [ ] Login returns access + refresh tokens
- [ ] Access token expires in 15 minutes
- [ ] Refresh token expires in 7 days
- [ ] Invalid credentials return 401
- [ ] Protected routes reject requests without valid token

---

#### AUTH-S2-002: RBAC Middleware Integration
**Priority:** P1 (High)  
**Est. Hours:** 8  
**Dependencies:** AUTH-S2-001  
**Owner:** TBD

```
Tasks:
1. Implement permission_required decorator
2. Wire permission hooks from app/api/hooks.py
3. Add role checks to all admin endpoints
4. Add role checks to customer-only endpoints
5. Return 403 for unauthorized access
```

---

### Frontend Integration

#### INT-S2-001: API Client Setup
**Priority:** P0 (Critical)  
**Est. Hours:** 6  
**Dependencies:** BE-S2-001  
**Owner:** TBD

```
Tasks:
1. Create /lib/api-client.ts with fetch wrapper
2. Add base URL configuration (env variable)
3. Add auth token handling
4. Add error handling/response parsing
5. Create typed API response interfaces
```

**File to create:** `UI/lib/api-client.ts`

---

#### INT-S2-002: Replace Mock Data with API Calls
**Priority:** P0 (Critical)  
**Est. Hours:** 16  
**Dependencies:** INT-S2-001, BE-S2-001 through BE-S2-004  
**Owner:** TBD

```
Tasks:
1. Update store-context.tsx to fetch from API
2. Replace sampleBooks with API call to GET /api/v1/books
3. Replace sampleSalesRecords with GET /api/v1/invoices
4. Replace samplePurchaseOrders with GET /api/v1/purchase-orders
5. Implement addToCart with POST to cart/invoice endpoint
6. Update inventory-page.tsx to fetch inventory
7. Update orders-page.tsx to fetch purchase orders
8. Update sales-page.tsx to fetch invoices
```

---

#### INT-S2-003: CORS Configuration
**Priority:** P0 (Critical)  
**Est. Hours:** 2  
**Dependencies:** None  
**Owner:** TBD

```
Tasks:
1. Install flask-cors
2. Configure CORS for localhost:3000 (dev)
3. Configure CORS for production domain
```

---

### Frontend Features (Remaining)

#### FE-S2-001: Admin Login Page
**Priority:** P1 (High)  
**Est. Hours:** 4  
**Dependencies:** AUTH-S2-001  
**Owner:** TBD

```
Tasks:
1. Create /app/login/page.tsx
2. Add login form (email, password)
3. Call auth API on submit
4. Store token in localStorage/cookie
5. Redirect to /admin on success
```

---

#### FE-S2-002: Customer Login/Register
**Priority:** P1 (High)  
**Est. Hours:** 6  
**Dependencies:** AUTH-S2-001  
**Owner:** TBD

```
Tasks:
1. Create /app/customer/login/page.tsx
2. Create /app/customer/register/page.tsx
3. Implement registration form
4. Implement login form
5. Store customer token
```

---

#### FE-S2-003: Admin Book Management (CRUD)
**Priority:** P1 (High)  
**Est. Hours:** 8  
**Dependencies:** INT-S2-002  
**Owner:** TBD

```
Tasks:
1. Add "Add New Book" dialog/form
2. Add "Edit Book" functionality
3. Add "Delete Book" confirmation
4. Wire all forms to API endpoints
```

---

#### FE-S2-004: Checkout Flow
**Priority:** P2 (Medium)  
**Est. Hours:** 10  
**Dependencies:** INT-S2-002, FE-S2-002  
**Owner:** TBD

```
Tasks:
1. Create /app/customer/checkout/page.tsx
2. Add shipping address form
3. Add payment method selection (mock)
4. Create invoice on order submission
5. Show order confirmation
```

---

### Testing

#### QA-S2-001: API Endpoint Tests
**Priority:** P1 (High)  
**Est. Hours:** 12  
**Dependencies:** BE-S2-001 through BE-S2-005  
**Owner:** TBD

```
Tasks:
1. Create tests/integration/test_books_api.py
2. Create tests/integration/test_inventory_api.py
3. Create tests/integration/test_invoices_api.py
4. Create tests/integration/test_purchase_orders_api.py
5. Create tests/integration/test_auth_api.py
```

---

#### QA-S2-002: Frontend Component Tests
**Priority:** P2 (Medium)  
**Est. Hours:** 8  
**Dependencies:** FE-S2-001 through FE-S2-004  
**Owner:** TBD

```
Tasks:
1. Set up Jest/React Testing Library
2. Test BookCatalog component
3. Test ShoppingCart component
4. Test InventoryPage component
```

---

## Sprint 2 Summary

### Total New Tasks: 15
### Total Estimated Hours: 130

| ID | Task | Hours | Priority | Owner |
|----|------|-------|----------|-------|
| BE-S2-001 | Books REST API | 8 | P0 | |
| BE-S2-002 | Inventory REST API | 10 | P0 | |
| BE-S2-003 | Invoices/Sales REST API | 12 | P1 | |
| BE-S2-004 | Purchase Orders REST API | 10 | P1 | |
| BE-S2-005 | Users/Customers REST API | 8 | P1 | |
| AUTH-S2-001 | JWT Authentication | 12 | P0 | |
| AUTH-S2-002 | RBAC Middleware | 8 | P1 | |
| INT-S2-001 | API Client Setup | 6 | P0 | |
| INT-S2-002 | Replace Mock Data | 16 | P0 | |
| INT-S2-003 | CORS Configuration | 2 | P0 | |
| FE-S2-001 | Admin Login Page | 4 | P1 | |
| FE-S2-002 | Customer Login/Register | 6 | P1 | |
| FE-S2-003 | Admin Book CRUD | 8 | P1 | |
| FE-S2-004 | Checkout Flow | 10 | P2 | |
| QA-S2-001 | API Endpoint Tests | 12 | P1 | |
| QA-S2-002 | Frontend Tests | 8 | P2 | |

---

## Sprint 3+ Roadmap

### Sprint 3 Focus: Advanced Features

| ID | Task | Est. Hours |
|----|------|------------|
| BE-S3-001 | Book Requests API | 6 |
| FE-S3-001 | Book Request Form (Customer) | 4 |
| FE-S3-002 | Book Request Management (Admin) | 6 |
| INT-S3-001 | Real-time Low Stock Alerts | 8 |
| QA-S3-001 | End-to-End Test Suite | 16 |

### Sprint 4 Focus: Polish & Production

| ID | Task | Est. Hours |
|----|------|------------|
| INF-S4-001 | Production Deployment Config | 8 |
| QA-S4-001 | Performance Testing | 8 |
| QA-S4-002 | Security Audit | 8 |
| DOC-S4-001 | User Documentation | 12 |
| DOC-S4-002 | API Documentation (OpenAPI) | 6 |

---

## Dependency Graph

```
                    ┌─────────────────┐
                    │  BE-S2-001      │
                    │  Books API      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ BE-S2-002  │  │ BE-S2-003  │  │ BE-S2-005  │
     │ Inventory  │  │ Invoices   │  │ Users API  │
     └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
           │               │               │
           └───────────────┼───────────────┘
                           ▼
                  ┌────────────────┐
                  │  AUTH-S2-001   │
                  │  JWT Auth      │
                  └────────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
     ┌────────────┐ ┌────────────┐ ┌────────────┐
     │ INT-S2-001 │ │AUTH-S2-002 │ │ FE-S2-001  │
     │ API Client │ │ RBAC       │ │ Login Page │
     └─────┬──────┘ └────────────┘ └────────────┘
           │
           ▼
     ┌────────────┐
     │ INT-S2-002 │
     │ Integration│
     └────────────┘
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API endpoints take longer than estimated | Medium | High | Start with Books API as proof of concept |
| Frontend integration issues | Medium | High | Set up CORS early, test with simple endpoint first |
| RBAC complexity | Low | Medium | Hooks already in place, just need wiring |
| Team availability | Unknown | High | Parallelize independent tasks |

---

## Immediate Action Items (This Week)

1. **Day 1-2:** Create BE-S2-001 (Books REST API) - This unblocks everything
2. **Day 2:** Create INT-S2-003 (CORS) - Quick win, needed for testing
3. **Day 3-4:** Create INT-S2-001 (API Client) - Enables frontend work
4. **Day 4-5:** Create AUTH-S2-001 (JWT) - Needed for protected routes

---

## Notes for Sprint Planning Meeting

1. **The backend SERVICE layer is complete** - we just need REST endpoints
2. **The frontend UI is complete** - we just need to wire it to real data
3. **The gap is the "glue"** - REST endpoints + API client + auth
4. **Parallelization opportunity:** Backend API work and frontend API client can happen simultaneously
5. **Suggestion:** Assign 2 people to backend (endpoints), 1 to frontend (client), 1 to auth

---

## File Locations Reference

### Backend (Flask)
- Services: `bookstore/app/services/`
- Models: `bookstore/app/models/`
- API Helpers: `bookstore/app/api/__init__.py`
- Hooks (RBAC): `bookstore/app/api/hooks.py`
- **NEW endpoints go in:** `bookstore/app/blueprints/` (create subdirectories)

### Frontend (Next.js)
- Pages: `UI/app/`
- Components: `UI/components/`
- Store/Context: `UI/lib/store-context.tsx`
- **NEW API client goes in:** `UI/lib/api-client.ts`

### Tests
- Unit: `bookstore/tests/unit/`
- Integration: `bookstore/tests/integration/`

---

**Document maintained by:** CS492 Group 4  
**Last updated:** 2026-05-18
