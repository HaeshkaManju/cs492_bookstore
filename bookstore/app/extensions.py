"""
Flask Extensions
================

This module initializes Flask extensions without binding them to
a specific application instance. Extensions are bound to the app
in the application factory via init_app().

This pattern allows:
    - Models to import db before the app exists
    - Multiple app instances (useful for testing)
    - Avoiding circular import issues

Usage in models:
    from app.extensions import db
    
    class User(db.Model):
        ...

Usage in app factory:
    from app.extensions import db, migrate
    
    def create_app():
        app = Flask(__name__)
        db.init_app(app)
        migrate.init_app(app, db)
        return app
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

db = SQLAlchemy()
"""
SQLAlchemy database instance.

Provides ORM functionality for database operations.
All models inherit from db.Model.

Example:
    class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(500), nullable=False)
"""

# -----------------------------------------------------------------------------
# Migrations
# -----------------------------------------------------------------------------

migrate = Migrate()
"""
Flask-Migrate instance for database migrations.

Wraps Alembic to provide database schema versioning.
Generates migration scripts automatically from model changes.

Commands:
    flask db init      - Initialize migrations folder
    flask db migrate   - Generate migration script
    flask db upgrade   - Apply migrations to database
    flask db downgrade - Revert last migration
"""

# -----------------------------------------------------------------------------
# Authentication
# -----------------------------------------------------------------------------

login_manager = LoginManager()
"""
Flask-Login instance for user session management.

Handles:
    - User session creation and validation
    - Login/logout functionality
    - "Remember me" functionality
    - Protecting views with @login_required

Configuration:
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
"""

# Configure login manager defaults
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please sign in to access this page.'
login_manager.login_message_category = 'info'
login_manager.refresh_view = 'auth.login'
login_manager.needs_refresh_message = 'Please re-authenticate to access this page.'
login_manager.needs_refresh_message_category = 'info'

# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------

csrf = CSRFProtect()
"""
CSRF protection instance.

Automatically protects all POST/PUT/DELETE forms with CSRF tokens.
Forms must include: {{ csrf_token() }} or use Flask-WTF forms.

The protection can be disabled per-view with @csrf.exempt decorator
for API endpoints that use alternative authentication.
"""
