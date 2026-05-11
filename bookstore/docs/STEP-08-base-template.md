# Step 8: Create Base Template

**Phase:** 0 - Foundation  
**File:** `app/templates/base.html`  
**Date:** 2026-05-06

---

## What We're Doing

Creating the base HTML template that all other templates will extend. This establishes:

1. **HTML Structure** - DOCTYPE, head, body layout
2. **Bootstrap 5** - CSS framework for styling
3. **Block System** - Jinja2 blocks for content injection
4. **Navigation Placeholder** - Will be role-based in Phase 5
5. **Flash Messages** - Display session messages

---

## Template Inheritance

```
base.html
├── auth/login.html      {% extends "base.html" %}
├── auth/register.html
├── admin/dashboard.html
├── inventory/list.html
└── customer/catalog.html
```

---

## Jinja2 Blocks

| Block | Purpose |
|-------|---------|
| `title` | Page title |
| `head` | Additional head content |
| `content` | Main page content |
| `scripts` | Additional JavaScript |

---

## Bootstrap 5 Features Used

- Container layout
- Navigation bar
- Alert components (for flash messages)
- Responsive grid
- Form styling

---

## Files Created

1. **`app/templates/base.html`** - Base template
2. **`app/templates/partials/flash.html`** - Flash messages partial
3. **`app/static/css/main.css`** - Custom styles
4. **`app/static/js/main.js`** - Custom JavaScript

---

## Git Commit

**Title:** `feat: add base template with Bootstrap 5`

**Message:**
```
Create base HTML template and static assets.

Templates created:
- base.html: Master template with Bootstrap 5 CDN
- partials/flash.html: Flash message display component

Static assets:
- css/main.css: Custom application styles
- js/main.js: Custom JavaScript utilities

Template features:
- Jinja2 template inheritance with blocks
- Bootstrap 5 via CDN for quick prototyping
- Flash message support with Bootstrap alerts
- Responsive container layout
- Placeholder navigation (to be enhanced in Phase 5)

Part of Phase 0: Foundation (Step 8/8) - PHASE COMPLETE
```

---

## Usage

```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
<h1>Hello World</h1>
{% endblock %}
```

---

## Dependencies

- Step 5 (app can render templates)

---

## Phase 0 Complete!

All foundation components are in place. The application can now:
- Start with `python run.py`
- Load environment-specific configuration
- Initialize Flask extensions
- Render templates with Bootstrap 5
- Run tests with pytest

**Next:** Phase 1 - Data Layer (Models)
