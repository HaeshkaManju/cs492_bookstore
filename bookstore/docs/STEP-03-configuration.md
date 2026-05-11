# Step 3: Create Configuration Classes

**Phase:** 0 - Foundation  
**File:** `app/config.py`  
**Date:** 2026-05-06

---

## What We're Doing

Creating environment-specific configuration classes using the class-based configuration pattern. This approach:

1. **Centralizes Settings** - All config in one file
2. **Supports Inheritance** - Base config with environment overrides
3. **Enables Environment Variables** - Sensitive data from environment
4. **Type Safety** - Class attributes are explicit

---

## Configuration Hierarchy

```
Config (Base)
├── DevelopmentConfig (debug enabled, local DB)
├── TestingConfig (testing flag, in-memory DB)
└── ProductionConfig (secure settings, real DB)
```

---

## Key Configuration Values

| Setting | Development | Testing | Production |
|---------|-------------|---------|------------|
| DEBUG | True | False | False |
| TESTING | False | True | False |
| DATABASE | PostgreSQL (local) | SQLite (memory) | PostgreSQL (real) |
| SECRET_KEY | Dev default | Test value | From environment |
| BCRYPT_ROUNDS | 4 (fast) | 4 (fast) | 12 (secure) |

---

## Security Considerations

- SECRET_KEY must be set from environment in production
- Database credentials from environment variables
- Never commit real secrets to version control
- Use .env file for local development (gitignored)

---

## File Created

**`app/config.py`** - Configuration classes

---

## Git Commit

**Title:** `feat: add environment-specific configuration classes`

**Message:**
```
Create configuration classes for development, testing, and production.

- Config (base): Common settings, loads from environment
- DevelopmentConfig: Debug enabled, local PostgreSQL
- TestingConfig: TESTING=True, SQLite in-memory for speed
- ProductionConfig: Secure defaults, requires env variables

Configuration features:
- Class-based inheritance pattern
- Environment variable support via os.environ
- Sensible defaults for development
- Strict requirements for production (SECRET_KEY)

Part of Phase 0: Foundation (Step 3/8)
```

---

## Test Verification

```python
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig

assert DevelopmentConfig.DEBUG == True
assert TestingConfig.TESTING == True
assert ProductionConfig.DEBUG == False
```

---

## Dependencies

- Step 2 (app factory loads config)

---

## Next Step

Step 4: Create Extensions Module (`app/extensions.py`)
