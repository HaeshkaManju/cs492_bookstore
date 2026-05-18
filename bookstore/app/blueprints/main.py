"""
Main Blueprint
==============

Contains the home page and basic status/health check routes.
"""

from flask import Blueprint, jsonify, render_template_string
from datetime import datetime

bp = Blueprint('main', __name__)


# Simple HTML template for the home page
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Bookstore Inventory Management</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
        }
        .container {
            text-align: center;
            padding: 2rem;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            color: #e94560;
        }
        .subtitle {
            color: #8892b0;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        .status-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 2rem;
            max-width: 500px;
            margin: 0 auto;
        }
        .status-row {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .status-row:last-child { border-bottom: none; }
        .status-label { color: #8892b0; }
        .status-value { color: #64ffda; font-weight: 500; }
        .status-value.ok { color: #64ffda; }
        .status-value.warn { color: #ffc107; }
        .api-links {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .api-links h3 {
            color: #8892b0;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .api-links a {
            display: inline-block;
            color: #64ffda;
            text-decoration: none;
            padding: 0.5rem 1rem;
            margin: 0.25rem;
            border: 1px solid #64ffda;
            border-radius: 4px;
            font-size: 0.85rem;
            transition: all 0.2s;
        }
        .api-links a:hover {
            background: #64ffda;
            color: #1a1a2e;
        }
        footer {
            margin-top: 2rem;
            color: #8892b0;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Bookstore API</h1>
        <p class="subtitle">Backend REST API Server</p>
        
        <div class="status-card">
            <div class="status-row" style="background: rgba(100,255,218,0.1); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border: 1px solid #64ffda;">
                <span class="status-label" style="color: #64ffda;">Frontend App</span>
                <span class="status-value ok"><a href="http://localhost:3000" style="color: #64ffda;">http://localhost:3000</a></span>
            </div>
            <div class="status-row">
                <span class="status-label">Application Status</span>
                <span class="status-value ok">Running</span>
            </div>
            <div class="status-row">
                <span class="status-label">Environment</span>
                <span class="status-value">{{ config }}</span>
            </div>
            <div class="status-row">
                <span class="status-label">Database</span>
                <span class="status-value {{ db_status_class }}">{{ db_status }}</span>
            </div>
            <div class="status-row">
                <span class="status-label">Server Time</span>
                <span class="status-value">{{ timestamp }}</span>
            </div>
            
            <div class="api-links">
                <h3>API Endpoints</h3>
                <a href="/api/v1/books">Books</a>
                <a href="/api/v1/inventory">Inventory</a>
                <a href="/api/v1/warehouses">Warehouses</a>
                <a href="/api/health">Health</a>
                <a href="/api/status">Status</a>
            </div>
        </div>
        
        <footer>
            CS492 Team Project - Bookstore Inventory Management System
        </footer>
    </div>
</body>
</html>
"""


@bp.route('/')
def home():
    """
    Home page - displays system status.
    
    This is a simple landing page to verify the application is running.
    """
    from flask import current_app
    from app.extensions import db
    
    # Check database connection
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = 'Connected'
        db_status_class = 'ok'
    except Exception as e:
        db_status = 'Disconnected'
        db_status_class = 'warn'
    
    return render_template_string(
        HOME_TEMPLATE,
        config=current_app.config.get('ENV', 'development'),
        db_status=db_status,
        db_status_class=db_status_class,
        timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    )


@bp.route('/api/health')
def health():
    """
    Health check endpoint.
    
    Returns simple JSON indicating the app is running.
    Used by load balancers, monitoring systems, etc.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


@bp.route('/api/status')
def status():
    """
    Detailed system status endpoint.
    
    Returns JSON with more detailed system information.
    """
    from flask import current_app
    from app.extensions import db
    
    # Check database
    try:
        db.session.execute(db.text('SELECT 1'))
        db_connected = True
    except Exception:
        db_connected = False
    
    # Get model counts if database is available
    counts = {}
    if db_connected:
        try:
            from app.models import Book, User, Inventory, Invoice
            counts = {
                'books': Book.query.count(),
                'users': User.query.count(),
                'inventory_items': Inventory.query.count(),
                'invoices': Invoice.query.count()
            }
        except Exception:
            pass
    
    return jsonify({
        'status': 'running',
        'environment': current_app.config.get('ENV', 'development'),
        'debug': current_app.debug,
        'database': {
            'connected': db_connected,
            'counts': counts
        },
        'timestamp': datetime.utcnow().isoformat()
    })
