"""
Application Configuration
=========================

This module contains configuration classes for different environments.
Configuration is loaded based on FLASK_ENV environment variable.

Usage:
    app.config.from_object('app.config.DevelopmentConfig')

Environment Variables:
    SECRET_KEY: Flask secret key for sessions and CSRF
    DATABASE_URL: PostgreSQL connection string
    BCRYPT_LOG_ROUNDS: Password hashing cost factor
"""

import os
from datetime import timedelta


class Config:
    """
    Base configuration with default settings.
    
    All environment-specific configs inherit from this class.
    Settings can be overridden via environment variables.
    """
    
    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database (PostgreSQL via SQLAlchemy)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://bookstore:bookstore_dev@localhost:5432/bookstore'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set True to log SQL queries
    
    # Security
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.environ.get('SESSION_LIFETIME_MINUTES', 60))
    )
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    REMEMBER_COOKIE_SECURE = False  # Set True in production
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Application Settings
    ITEMS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    
    # Invoice Settings
    INVOICE_NUMBER_PREFIX = 'INV'
    DEFAULT_PAYMENT_TERMS = 'Net 30'
    
    # Book Request Settings
    REQUEST_EXPIRY_DAYS = 365  # Requests expire after 1 year
    
    # Condition Grades (for reference)
    CONDITION_GRADES = {
        5: 'Fine',
        4: 'Very Good',
        3: 'Good',
        2: 'Fair',
        1: 'Poor'
    }


class DevelopmentConfig(Config):
    """
    Development configuration.
    
    Enables debug mode and uses SQLite for simple local development.
    Optimized for rapid development with verbose output.
    """
    
    DEBUG = True
    TESTING = False
    
    # Faster password hashing for development
    BCRYPT_LOG_ROUNDS = 4
    
    # Show SQL queries in console (set False to reduce noise)
    SQLALCHEMY_ECHO = False
    
    # Development database - SQLite for simplicity
    # Uses instance folder for database file
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///bookstore_dev.db'
    )


class TestingConfig(Config):
    """
    Testing configuration.
    
    Uses SQLite in-memory database for fast test execution.
    Disables CSRF for easier form testing.
    """
    
    DEBUG = False
    TESTING = True
    
    # In-memory SQLite for fast tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4
    
    # Disable CSRF for testing (easier form submissions)
    WTF_CSRF_ENABLED = False
    
    # Preserve exceptions for test assertions
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Fixed secret key for consistent test sessions
    SECRET_KEY = 'test-secret-key-not-for-production'


class ProductionConfig(Config):
    """
    Production configuration.
    
    Enforces security requirements and uses environment variables
    for all sensitive settings. Will raise error if SECRET_KEY
    is not properly set.
    """
    
    DEBUG = False
    TESTING = False
    
    # Require SECRET_KEY from environment
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @classmethod
    def init_app(cls, app):
        """Validate production configuration."""
        if not cls.SECRET_KEY:
            raise ValueError(
                'SECRET_KEY environment variable must be set in production'
            )
        
        # Ensure secure cookies over HTTPS
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['REMEMBER_COOKIE_SECURE'] = True
    
    # Production database from environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Full security for passwords
    BCRYPT_LOG_ROUNDS = 12
    
    # Secure session settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


# Configuration dictionary for easy lookup
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
