# Project Folder Structure

## Current Structure vs. Planned Structure

### What the Architecture Documents Planned

**01-SYSTEM-OVERVIEW.md** (original plan):
```
bookstore-inventory/
├── backend/          # Python FastAPI
├── frontend/         # React.js + TypeScript
├── database/
└── docs/
```

**01-REVISED-ARCHITECTURE.md** (revised plan):
```
bookstore/
├── app/              # Flask with Jinja2 templates (server-side rendering)
├── templates/        # Jinja2 HTML templates
├── static/           # CSS, JS
└── tests/
```

### What Actually Exists

```
cs492_bookstore/
├── bookstore/        # Flask backend (API + services)
│   ├── app/
│   │   ├── models/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── blueprints/api/    # REST API endpoints
│   │   └── templates/         # (mostly empty - not using Jinja2)
│   └── tests/
│
├── frontend/         # React/Next.js frontend (separate SPA)
│   ├── app/          # Next.js pages
│   ├── components/
│   └── lib/          # API client, contexts
│
├── architecture/     # Design documents (including beginning_sprint1, beginning_sprint2)
│   ├── beginning_sprint1/   # Sprint 1 planning docs
│   ├── beginning_sprint2/   # Sprint 2 planning docs (FOLDER_STRUCTURE, SPRINT2_COMPLETION_PLAN, TEST_ACCOUNTS)
│   └── diagrams/            # Architecture diagrams
└── unit_tests/       # Legacy tests folder
```

## Analysis: Should UI Be Integrated?

### Option A: Keep Separate (Current State) - RECOMMENDED

**Pros:**
- Clean separation of concerns (API backend + SPA frontend)
- Each can be deployed independently
- Frontend team can work without affecting backend
- Modern architecture pattern (decoupled)
- Allows for multiple clients (web, mobile) using same API

**Cons:**
- Deviates from original architecture docs
- CORS required for development
- Two package managers (pip + pnpm)

### Option B: Move UI into bookstore/frontend/

```
bookstore/
├── app/              # Flask backend
├── frontend/         # React frontend (renamed from UI)
└── tests/
```

**Pros:**
- Matches original architecture doc
- Single repository root

**Cons:**
- Still two separate applications
- No real integration benefit

### Option C: Return to Jinja2 Templates (Original Revised Plan)

**Pros:**
- Matches revised architecture document
- Single deployment
- No CORS issues

**Cons:**
- Discard all React work (~40+ components)
- Server-side rendering is less interactive
- Significant rework

## Recommendation

**Keep the current structure (Option A)** with these clarifications:

1. ~~**Rename `UI/` to `frontend/`**~~ - DONE
2. **Update architecture docs** - Document the actual implementation
3. **This is a valid architectural decision** - API + SPA is a modern, scalable pattern

The React frontend was built as a UI/UX design exploration and provides a more modern user experience than Jinja2 templates would have.

## Running the Applications

### Backend (Flask API)
```bash
cd bookstore
pip install -r requirements.txt
python run.py
# API available at http://localhost:5000/api/v1/
```

### Frontend (Next.js)
```bash
cd frontend
pnpm install
pnpm dev
# App available at http://localhost:3000
```

### Running Tests
```bash
cd bookstore
python run_tests.py
# or
pytest tests/ -v
```

## Environment Configuration

### Backend (.env in bookstore/)
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/bookstore
```

### Frontend (.env.local in frontend/)
```
NEXT_PUBLIC_API_URL=http://localhost:5000/api/v1
```
