# Step 2: Create Application Factory

**Phase:** 0 - Foundation  
**File:** `app/__init__.py`  
**Date:** 2026-05-06

---

## What We're Doing

Implementing the Application Factory pattern for Flask. This is the recommended approach because it:

1. **Enables Testing** - Create fresh app instances for each test
2. **Supports Multiple Configs** - Different settings for dev/test/prod
3. **Avoids Circular Imports** - Extensions initialized without app instance
4. **Enables Blueprints** - Modular route registration

---

## The Application Factory Pattern

```python
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Initialize extensions
    # Register blueprints
    # Set up error handlers
    
    return app
```

At this stage, we create the skeleton. Extensions and blueprints will be added in subsequent steps.

---

## Files Created

1. **`app/__init__.py`** - Application factory function
2. **`app/blueprints/__init__.py`** - Blueprints package init
3. **`app/models/__init__.py`** - Models package init
4. **`app/services/__init__.py`** - Services package init
5. **`app/utils/__init__.py`** - Utils package init

---

## Git Commit

**Title:** `feat: implement application factory pattern`

**Message:**
```
Create the Flask application factory in app/__init__.py.

- Implement create_app() function with config parameter
- Set up instance-relative configuration
- Create package __init__.py files for all modules
- Prepare structure for extension initialization (Step 4)
- Prepare structure for blueprint registration (Phase 4)

The application factory pattern enables:
- Multiple app instances for testing
- Environment-specific configuration
- Clean separation of concerns

Part of Phase 0: Foundation (Step 2/8)
```

---

## Test Verification

```python
from app import create_app
app = create_app('testing')
assert app is not None
assert app.config['TESTING'] == True
```

---

## Dependencies

- Step 1 (run.py references create_app)

---

## Next Step

Step 3: Create Configuration Classes (`app/config.py`)
