"""
Bookstore Inventory Management System
======================================

A Flask-based inventory management system for rare bookstores.

This module contains the application factory function that creates
and configures the Flask application instance.
"""

import os
from flask import Flask

from app.extensions import db, migrate, login_manager, csrf
from app.config import config


def create_app(config_name: str = 'development') -> Flask:
    """
    Create and configure the Flask application.
    
    This factory function creates a new Flask application instance
    configured for the specified environment.
    
    Args:
        config_name: Configuration environment to use.
                     Options: 'development', 'testing', 'production'
                     Defaults to 'development'.
    
    Returns:
        Flask: Configured Flask application instance.
    
    Example:
        >>> app = create_app('testing')
        >>> app.config['TESTING']
        True
    """
    # Create Flask instance with instance folder support
    # Instance folder stores local config that shouldn't be in version control
    app = Flask(
        __name__,
        instance_relative_config=True
    )
    
    # Load configuration based on environment
    config_class = config.get(config_name, config['default'])
    app.config.from_object(config_class)
    
    # Run production-specific initialization if needed
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize Flask extensions
    _init_extensions(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Error handlers will be registered here (Step 48)
    # _register_error_handlers(app)
    
    # Register context processors for templates
    _register_context_processors(app)
    
    # Shell context for flask shell command
    @app.shell_context_processor
    def make_shell_context():
        """Add useful items to flask shell context."""
        return {
            'app': app,
            'db': db,
            # Models will be added here as they are created
        }
    
    return app


def _init_extensions(app: Flask) -> None:
    """
    Initialize Flask extensions with the application instance.
    
    Extensions are created in extensions.py without an app instance,
    then bound to the app here using init_app().
    
    Args:
        app: Flask application instance
    """
    # Database ORM
    db.init_app(app)
    
    # Database migrations
    migrate.init_app(app, db)
    
    # User authentication
    login_manager.init_app(app)
    
    # CSRF protection
    csrf.init_app(app)
    
    # Set up user loader for Flask-Login
    # This callback loads a user from the database given their ID
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login session management."""
        # Import here to avoid circular imports
        # User model will be created in Phase 1 (Step 10)
        try:
            from app.models.user import User
            return User.query.get(user_id)
        except ImportError:
            # User model not yet created
            return None


def _register_blueprints(app: Flask) -> None:
    """
    Register Flask blueprints with the application.
    
    Blueprints organize routes by feature area.
    
    Args:
        app: Flask application instance
    """
    from app.blueprints.main import bp as main_bp
    
    # Main blueprint (home, health checks)
    app.register_blueprint(main_bp)
    
    # Additional blueprints will be registered as they are created:
    # from app.blueprints.auth import bp as auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    #
    # from app.blueprints.inventory import bp as inventory_bp
    # app.register_blueprint(inventory_bp, url_prefix='/inventory')


def _register_context_processors(app: Flask) -> None:
    """
    Register template context processors.
    
    Context processors make variables available in all templates
    without explicitly passing them from each route.
    
    Args:
        app: Flask application instance
    """
    @app.context_processor
    def inject_config():
        """Make configuration values available in templates."""
        return {
            'condition_grades': app.config.get('CONDITION_GRADES', {}),
        }
    
    @app.context_processor
    def inject_utilities():
        """Make utility functions available in templates."""
        def format_condition(condition_value):
            """Convert condition integer to label."""
            grades = app.config.get('CONDITION_GRADES', {})
            return grades.get(condition_value, 'Unknown')
        
        return {
            'format_condition': format_condition,
        }
