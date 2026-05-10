# Bookstore Inventory Management System
## System Reference Document Index

**Project:** Bookstore Inventory Management System  
**Course:** CS491/CS492 - Team Project  
**Group:** #4 
**Last Updated:** 2026-05-05

---

## Document Navigation

| Document | Description | Key Stories/Tasks |
|----------|-------------|-------------------|
| [01-SYSTEM-OVERVIEW](01-SYSTEM-OVERVIEW.md) | Vision, scope, technology stack, high-level architecture | All |
| [02-DATA-LAYER](02-DATA-LAYER.md) | Database schema, entities, relationships, migrations | S1-9 to S1-14, US-002 |
| [03-AUTHENTICATION](03-AUTHENTICATION.md) | JWT auth, roles, permissions, security controls | S1-15 to S1-21, US-003 |
| [04-INVENTORY-MODULE](04-INVENTORY-MODULE.md) | Inventory management subsystem | S2-6 to S2-11, US-005 |
| [05-SALES-MODULE](05-SALES-MODULE.md) | Sales records and reporting subsystem | US-006 |
| [06-PURCHASE-ORDERS](06-PURCHASE-ORDERS.md) | Manufacturer ordering subsystem | US-007 |
| [07-CUSTOMER-PORTAL](07-CUSTOMER-PORTAL.md) | Public-facing customer interface | US-008 |
| [08-API-REFERENCE](08-API-REFERENCE.md) | REST API endpoint specifications | S2-7, All backend tasks |
| [09-TESTING-QA](09-TESTING-QA.md) | Testing strategy, QA processes | US-009, US-010 |
| [10-SPRINT-TRACEABILITY](10-SPRINT-TRACEABILITY.md) | Sprint-to-architecture mapping matrix | All |

---

## Quick Reference: Story IDs

| Story ID | Title | Primary Module |
|----------|-------|----------------|
| US-001 | Project Setup and Repository Initialization | Infrastructure |
| US-002 | Database Schema Design and Implementation | Data Layer |
| US-003 | User Authentication and Authorization System | Authentication |
| US-004 | Admin Dashboard Framework | Frontend |
| US-005 | Inventory Management Module | Inventory |
| US-006 | Sales Records Module | Sales |
| US-007 | Purchase Order System | Purchase Orders |
| US-008 | Customer Portal Interface | Customer Portal |
| US-009 | Integration Testing and Quality Assurance | Testing |
| US-010 | System Performance and Usability Optimization | Non-Functional |
| US-011 | Data Backup and Integrity System | Data Layer |
| US-012 | User and Technical Documentation | Documentation |

---

## Architecture Principles

1. **Separation of Concerns** - Each module is self-contained with clear interfaces
2. **Testability** - Every component designed for unit and integration testing
3. **Security First** - Role-based access control at every layer
4. **Python/FastAPI** - Backend standardized on Python with FastAPI framework
5. **PostgreSQL** - Relational database with ACID compliance

---

## Source Documents

- `CS491 - Bookstore Inventory Management _.docx` - Project vision, Definition of Done, Product Design
- `CS491 Sprint_Planning_Document _.xlsx` - Sprint backlog, task breakdown, assignments
