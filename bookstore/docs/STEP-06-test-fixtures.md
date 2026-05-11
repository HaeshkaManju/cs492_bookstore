# Step 6: Create Base Test Fixtures

**Phase:** 0 - Foundation  
**File:** `tests/conftest.py`  
**Date:** 2026-05-06

---

## What We're Doing

Creating pytest fixtures that provide a consistent testing environment. Fixtures are reusable test setup components that:

1. **Create Test App** - Fresh app instance for each test session
2. **Provide Test Client** - Simulates HTTP requests
3. **Manage Database** - Creates/drops tables for each test
4. **Enable CLI Testing** - Test Flask CLI commands

---

## Fixture Scopes

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `app` | session | Create app once per test run |
| `client` | function | Fresh client for each test |
| `db_session` | function | Database session with rollback |
| `runner` | function | CLI test runner |

---

## Test Database Strategy

Tests use SQLite in-memory database for speed:
- Created fresh for each test session
- Tables created via `db.create_all()`
- Transactions rolled back between tests
- No PostgreSQL required for unit tests

---

## Files Created

1. **`tests/__init__.py`** - Tests package init
2. **`tests/conftest.py`** - Shared pytest fixtures
3. **`tests/unit/__init__.py`** - Unit tests package
4. **`tests/integration/__init__.py`** - Integration tests package

---

## Git Commit

**Title:** `feat: add pytest fixtures and test infrastructure`

**Message:**
```
Create pytest fixtures for testing infrastructure.

Files created:
- tests/conftest.py: Shared fixtures for all tests
- tests/__init__.py: Tests package initialization
- tests/unit/__init__.py: Unit tests package
- tests/integration/__init__.py: Integration tests package

Fixtures provided:
- app: Flask application with TestingConfig
- client: Test client for HTTP request simulation
- db_session: Database session with automatic rollback
- runner: CLI test runner for flask commands

Testing strategy:
- Use SQLite in-memory for unit tests (fast)
- Transactions rolled back after each test (isolation)
- Session-scoped app creation (efficiency)

Part of Phase 0: Foundation (Step 6/8)
```

---

## Test Verification

```bash
# Run from bookstore directory
pytest tests/ -v
```

Should show "no tests collected" (tests not yet written).

---

## Dependencies

- Step 5 (functional app factory)

---

## Next Step

Step 7: Create .env.example Template
