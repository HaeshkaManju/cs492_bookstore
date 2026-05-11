# Step 4: Create Extensions Module

**Phase:** 0 - Foundation  
**File:** `app/extensions.py`  
**Date:** 2026-05-06

---

## What We're Doing

Creating Flask extensions as module-level singletons that are initialized without the app instance. This pattern:

1. **Avoids Circular Imports** - Extensions exist before app
2. **Enables Lazy Initialization** - init_app() called later
3. **Supports Multiple Apps** - Each app binds independently
4. **Simplifies Imports** - `from app.extensions import db`

---

## Extensions Used

| Extension | Purpose | Package |
|-----------|---------|---------|
| SQLAlchemy | Database ORM | Flask-SQLAlchemy |
| Migrate | Database migrations | Flask-Migrate |
| LoginManager | User sessions | Flask-Login |
| CSRFProtect | CSRF protection | Flask-WTF |

---

## The Extension Pattern

```python
# Create without app
db = SQLAlchemy()

# Later, in create_app():
db.init_app(app)
```

This two-phase initialization allows:
- Models to import `db` before app exists
- Tests to create fresh app instances
- Multiple apps (rare, but possible)

---

## File Created

**`app/extensions.py`** - Extension instances

---

## Git Commit

**Title:** `feat: add Flask extensions module`

**Message:**
```
Create extensions.py with Flask extension instances.

Extensions initialized:
- SQLAlchemy (db): Database ORM for PostgreSQL
- Migrate (migrate): Alembic-based migrations
- LoginManager (login_manager): User session management
- CSRFProtect (csrf): Form CSRF protection

Extensions are created without app instance and will be
bound via init_app() in the application factory (Step 5).

This pattern enables:
- Clean model imports without circular dependencies
- Multiple app instances for testing
- Lazy initialization with configuration

Part of Phase 0: Foundation (Step 4/8)
```

---

## Test Verification

```python
from app.extensions import db, migrate, login_manager, csrf

assert db is not None
assert migrate is not None
assert login_manager is not None
assert csrf is not None
```

---

## Dependencies

- Step 3 (config provides database URI)

---

## Next Step

Step 5: Wire Extensions to Application Factory
