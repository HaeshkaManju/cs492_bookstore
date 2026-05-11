"""
Application Entry Point
=======================

This module serves as the main entry point for the Bookstore Inventory
Management System. It creates and runs the Flask application.

Usage:
    Development server:
        $ python run.py
        
    With Flask CLI:
        $ set FLASK_APP=run.py
        $ flask run

    Production (with gunicorn):
        $ gunicorn "run:app"
"""

import os

from app import create_app

# Determine configuration from environment
# Options: 'development', 'testing', 'production'
config_name = os.environ.get('FLASK_ENV', 'development')

# Create the application instance
app = create_app(config_name)

if __name__ == '__main__':
    # Run development server
    # Debug mode is enabled automatically for 'development' config
    app.run(
        host=os.environ.get('FLASK_HOST', '127.0.0.1'),
        port=int(os.environ.get('FLASK_PORT', 5000))
    )
