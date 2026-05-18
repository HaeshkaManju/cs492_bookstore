"""
API Blueprint Package
=====================

REST API endpoints for the Bookstore system.
All endpoints are prefixed with /api/v1/
"""

from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api/v1')

from app.blueprints.api import books, inventory, invoices, purchase_orders, users, auth
