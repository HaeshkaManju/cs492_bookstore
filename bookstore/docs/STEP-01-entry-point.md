# Step 1: Create Application Entry Point

**Phase:** 0 - Foundation  
**File:** `run.py`  
**Date:** 2026-05-06

---

## What We're Doing

Creating the main entry point for the Flask application. This file serves as:
1. The script that starts the development server (`python run.py`)
2. The target for `FLASK_APP` environment variable (`flask run`)
3. The entry point for WSGI servers in production

At this stage, we create a minimal skeleton that will be expanded as we add the application factory.

---

## Implementation Details

The `run.py` file:
- Imports the application factory (to be created in Step 2)
- Reads configuration from environment variables
- Creates the Flask app instance
- Runs the development server when executed directly

For now, we create a placeholder that will be functional once the app factory exists.

---

## File Created

**`run.py`** - Application entry point

---

## Git Commit

**Title:** `feat: add application entry point (run.py)`

**Message:**
```
Add the main entry point for the Flask application.

- Creates run.py as the primary way to start the server
- Reads FLASK_ENV from environment (defaults to 'development')
- Prepares for application factory pattern (Step 2)
- Enables both `python run.py` and `flask run` execution

Part of Phase 0: Foundation (Step 1/8)
```

---

## Test Verification

After Step 2, verify with:
```bash
python -c "from run import app; print(type(app))"
```

Expected: `<class 'flask.app.Flask'>`

---

## Dependencies

- None (first step)

---

## Next Step

Step 2: Create Application Factory (`app/__init__.py`)
