# Step 5: Wire Extensions to Application Factory

**Phase:** 0 - Foundation  
**File:** `app/__init__.py` (update)  
**Date:** 2026-05-06

---

## What We're Doing

Updating the application factory to:

1. **Load Configuration Properly** - Use the config dictionary
2. **Initialize Extensions** - Call init_app() for each extension
3. **Set Up User Loader** - Required callback for Flask-Login
4. **Add Context Processors** - Make utilities available in templates

---

## Extension Initialization Order

Extensions must be initialized in the correct order:

1. **db** (SQLAlchemy) - First, as other extensions may depend on it
2. **migrate** (Flask-Migrate) - Needs db instance
3. **login_manager** (Flask-Login) - Needs db for user loader
4. **csrf** (CSRFProtect) - Last, wraps the entire app

---

## User Loader Function

Flask-Login requires a callback to load users from the database:

```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
```

This is called on every request to verify the session.

---

## File Updated

**`app/__init__.py`** - Added extension initialization

---

## Git Commit

**Title:** `feat: wire extensions to application factory`

**Message:**
```
Update app factory to initialize all Flask extensions.

Changes to app/__init__.py:
- Import extensions from app.extensions
- Import configuration dictionary from app.config
- Add _init_extensions() helper function
- Initialize db, migrate, login_manager, csrf
- Add user_loader callback for Flask-Login
- Add context processors for templates
- Call ProductionConfig.init_app() for production

The application is now fully functional with:
- Database connectivity (SQLAlchemy)
- Migration support (Flask-Migrate)
- User session management (Flask-Login)
- CSRF protection (Flask-WTF)

Part of Phase 0: Foundation (Step 5/8)
```

---

## Test Verification

```python
from app import create_app
from app.extensions import db

app = create_app('testing')
with app.app_context():
    # Database should be accessible
    assert db.engine is not None
```

---

## Dependencies

- Step 3 (configuration classes)
- Step 4 (extension instances)

---

## Next Step

Step 6: Create Base Test Fixtures (`tests/conftest.py`)
