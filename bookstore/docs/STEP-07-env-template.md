# Step 7: Create .env.example Template

**Phase:** 0 - Foundation  
**Files:** `.env.example`, `.gitignore`, `requirements.txt`, `requirements-dev.txt`  
**Date:** 2026-05-06

---

## What We're Doing

Creating essential project files:

1. **`.env.example`** - Template for environment variables
2. **`.gitignore`** - Prevent sensitive files from being committed
3. **`requirements.txt`** - Production dependencies
4. **`requirements-dev.txt`** - Development dependencies

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| FLASK_APP | No | Entry point (default: run.py) |
| FLASK_ENV | No | Environment (development/production) |
| SECRET_KEY | Yes (prod) | Session encryption key |
| DATABASE_URL | Yes (prod) | PostgreSQL connection string |
| BCRYPT_LOG_ROUNDS | No | Password hashing cost (default: 12) |

---

## Gitignore Strategy

Never commit:
- `.env` (contains secrets)
- `instance/` (local configuration)
- `__pycache__/` (compiled Python)
- `.pytest_cache/` (test cache)
- `*.pyc` (compiled files)
- `.coverage` (coverage data)

---

## Files Created

1. **`.env.example`** - Environment template
2. **`.gitignore`** - Git ignore rules
3. **`requirements.txt`** - Production dependencies
4. **`requirements-dev.txt`** - Development dependencies

---

## Git Commit

**Title:** `chore: add environment template and dependencies`

**Message:**
```
Add essential project configuration files.

Files created:
- .env.example: Template for environment variables with documentation
- .gitignore: Comprehensive ignore rules for Python/Flask project
- requirements.txt: Production dependencies (Flask, SQLAlchemy, etc.)
- requirements-dev.txt: Development tools (pytest, black, flake8)

Security notes:
- .env file (actual secrets) is gitignored
- instance/ folder for local config is gitignored
- All sensitive file patterns excluded

Part of Phase 0: Foundation (Step 7/8)
```

---

## Usage

```bash
# Copy template to actual .env file
cp .env.example .env

# Edit .env with your local settings
# Never commit .env!

# Install dependencies
pip install -r requirements-dev.txt
```

---

## Dependencies

- Step 3 (config expects these environment variables)

---

## Next Step

Step 8: Create Base Template (`app/templates/base.html`)
