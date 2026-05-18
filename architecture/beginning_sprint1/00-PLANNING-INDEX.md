# Bookstore Project - Detailed Planning Index

**Project:** Bookstore Inventory Management System  
**Framework:** Flask (Python)  
**Database:** PostgreSQL  
**Business Model:** Invoice-based rare bookstore (no online payments)

---

## Architecture Changes from Original

| Original | Updated |
|----------|---------|
| FastAPI | Flask |
| React.js frontend | Flask templates (Jinja2) + minimal JS |
| Online payments | Invoice generation only |
| Standard retail | Rare book clientele with request system |

---

## Planning Structure

```
planning/
├── 00-PLANNING-INDEX.md          # This file
├── 01-REVISED-ARCHITECTURE.md    # Updated tech stack & business model
├── sprint1/
│   ├── week1/                    # ✓ COMPLETE (8 tasks)
│   │   ├── S1-01-repo-setup.md           # Repository initialization
│   │   ├── S1-02-folder-structure.md     # Flask project skeleton
│   │   ├── S1-03-branching-strategy.md   # GitFlow workflow
│   │   ├── S1-04-dev-environment.md      # Docker, venv, config
│   │   ├── S1-05-setup-docs.md           # Developer documentation
│   │   ├── S1-06-team-access.md          # Access verification
│   │   ├── S1-07-sprint-planning.md      # Sprint plan template
│   │   └── S1-08-cicd-pipeline.md        # GitHub Actions CI/CD
│   └── week2/                    # ✓ COMPLETE (13 tasks)
│       ├── S1-09-erd-design.md           # ERD with all tables
│       ├── S1-10-sql-scripts.md          # Complete DDL scripts
│       ├── S1-11-validation-rules.md     # Input validators
│       ├── S1-12-migrations.md           # Flask-Migrate setup
│       ├── S1-13-db-connection.md        # SQLAlchemy configuration
│       ├── S1-14-schema-docs.md          # Database documentation
│       ├── S1-15-roles-design.md         # RBAC permission matrix
│       ├── S1-16-registration.md         # Customer registration
│       ├── S1-17-login.md                # Login/session management
│       ├── S1-18-password-hashing.md     # bcrypt password security
│       ├── S1-19-rbac-middleware.md      # Role-based decorators
│       ├── S1-20-route-guards.md         # Blueprint protection
│       └── S1-21-customer-flow.md        # Customer portal flow
├── tests/
│   ├── conftest.py               # Shared fixtures
│   ├── test_runner.py            # Test suite runner with reporting
│   ├── auth/                     # Authentication tests
│   ├── database/                 # Database tests
│   ├── inventory/                # Inventory tests
│   ├── sales/                    # Sales tests
│   ├── orders/                   # Order/invoice tests
│   └── integration/              # Cross-module tests
└── code_segments/
    ├── segment_index.md          # Index of all code segments
    └── sprint1/                  # Code delivered per sprint
```

---

## Business Model Summary

### Invoice-Based Rare Bookstore

1. **No Online Payments**
   - System generates invoices, not payment processing
   - Customers are established clientele
   - Payment handled outside the system

2. **Book Request System**
   - Customers can request books not currently in inventory
   - Request includes desired condition (Fine, Very Good, Good, Fair, Poor)
   - System notifies when matching book becomes available

3. **Invoice Features**
   - Professional invoice template
   - Pending items noted: "When available in requested condition, we will notify you"
   - Track invoice status (Draft, Sent, Paid, Cancelled)

---

## Key Files to Protect (.gitignore)

- `config/secrets.py` - API keys, DB credentials
- `instance/` - Flask instance folder
- `.env` - Environment variables
- `*.pem`, `*.key` - SSL certificates
- `tests/fixtures/sensitive/` - Test data with PII

---

## Sprint Overview

| Sprint | Focus | Status |
|--------|-------|--------|
| Sprint 1 | Setup, Database, Auth | **Detailed Tasks Complete** |
| Sprint 2 | Admin Dashboard, Inventory | Planned |
| Sprint 3 | Sales, Purchase Orders | Planned |
| Sprint 4 | Customer Portal, Invoicing | Planned |
| Sprint 5 | Testing, Polish, Deploy | Planned |

---

## Sprint 1 Task Summary

### Week 1: Setup (8 Tasks)

| Task | Title | Owner | Status |
|------|-------|-------|--------|
| S1-01 | Repository Setup | C. Michael Fisher | ⬜ Pending |
| S1-02 | Folder Structure | C. Michael Fisher | ⬜ Pending |
| S1-03 | Branching Strategy | Rich Harris | ⬜ Pending |
| S1-04 | Dev Environment | All | ⬜ Pending |
| S1-05 | Setup Documentation | C. Michael Fisher | ⬜ Pending |
| S1-06 | Team Access Verification | All | ⬜ Pending |
| S1-07 | Sprint Planning Meeting | All | ⬜ Pending |
| S1-08 | CI/CD Pipeline | Rich Harris | ⬜ Pending |

### Week 2: Database & Auth (13 Tasks)

| Task | Title | Owner | Status |
|------|-------|-------|--------|
| S1-09 | ERD Design | C. Michael Fisher | ⬜ Pending |
| S1-10 | SQL Scripts | C. Michael Fisher | ⬜ Pending |
| S1-11 | Validation Rules | C. Michael Fisher | ⬜ Pending |
| S1-12 | Migrations Setup | C. Michael Fisher | ⬜ Pending |
| S1-13 | Database Connection | C. Michael Fisher | ⬜ Pending |
| S1-14 | Schema Documentation | C. Michael Fisher | ⬜ Pending |
| S1-15 | Roles & Permissions | Willie Idolor | ⬜ Pending |
| S1-16 | User Registration | Willie Idolor | ⬜ Pending |
| S1-17 | Login & Session | Willie Idolor | ⬜ Pending |
| S1-18 | Password Hashing | Willie Idolor | ⬜ Pending |
| S1-19 | RBAC Middleware | Willie Idolor | ⬜ Pending |
| S1-20 | Route Guards | Willie Idolor | ⬜ Pending |
| S1-21 | Customer Portal Flow | Willie Idolor | ⬜ Pending |

---

## Quick Start for Team

1. **Clone Repository** (after S1-01)
   ```bash
   git clone https://github.com/your-team/bookstore-inventory.git
   cd bookstore-inventory
   ```

2. **Set Up Environment** (S1-04)
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements-dev.txt
   cp .env.example .env
   ```

3. **Start Database** (Docker)
   ```bash
   docker-compose up -d postgres
   ```

4. **Run Migrations** (after S1-12)
   ```bash
   flask db upgrade
   ```

5. **Run Application**
   ```bash
   flask run
   ```

6. **Run Tests**
   ```bash
   pytest
