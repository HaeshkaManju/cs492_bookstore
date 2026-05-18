"""
Books API Endpoints
===================

REST API for book catalog management.
Task: BE-S2-001
"""

from flask import request, jsonify
from uuid import UUID

from app.blueprints.api import bp
from app.blueprints.api.auth import jwt_required, staff_required, admin_required
from app.api import get_book_service, api_success, api_error, api_validation_error, api_not_found
from app.services.base import ValidationError, NotFoundError, ConflictError
from app.schemas import BookSchema


@bp.route('/books', methods=['GET'])
def list_books():
    """
    List and search books.
    
    Query params:
        q: Search query (title, author, ISBN)
        category: Filter by category
        in_stock_only: Only books with inventory (true/false)
        page: Page number (default 1)
        per_page: Items per page (default 20, max 100)
    """
    service = get_book_service()
    
    query = request.args.get('q', '')
    category = request.args.get('category')
    in_stock_only = request.args.get('in_stock_only', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    results = service.search(
        query=query,
        category=category,
        in_stock_only=in_stock_only,
        page=page,
        per_page=per_page
    )
    
    books_data = [BookSchema.from_model(book).to_dict() for book in results['items']]
    
    return jsonify({
        'success': True,
        'data': books_data,
        'pagination': {
            'total': results['total'],
            'page': results['page'],
            'per_page': results['per_page'],
            'pages': results['pages'],
            'has_next': results['page'] < results['pages'],
            'has_prev': results['page'] > 1
        }
    }), 200


@bp.route('/books/<uuid:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a single book by ID with optional inventory stats."""
    service = get_book_service()
    
    include_inventory = request.args.get('include_inventory', 'true').lower() == 'true'
    
    try:
        if include_inventory:
            book = service.get_with_inventory(book_id)
        else:
            book = service.get_by_id(book_id)
        
        if not book:
            return api_not_found('Book', str(book_id))
        
        book_data = BookSchema.from_model(book, include_inventory_stats=include_inventory).to_dict()
        return api_success(data=book_data)
        
    except NotFoundError as e:
        return api_not_found('Book', str(book_id))


@bp.route('/books', methods=['POST'])
@staff_required
def create_book():
    """
    Create a new book.
    
    Request body:
        title: Book title (required)
        author: Author name (required)
        isbn: ISBN (optional)
        publisher: Publisher name (optional)
        year_published: Publication year (optional)
        description: Book description (optional)
        category: Book category (optional)
    """
    service = get_book_service()
    data = request.get_json() or {}
    
    try:
        book = service.create_book(
            title=data.get('title', ''),
            author=data.get('author', ''),
            isbn=data.get('isbn'),
            publisher=data.get('publisher'),
            year_published=data.get('year_published'),
            description=data.get('description'),
            category=data.get('category')
        )
        
        book_data = BookSchema.from_model(book).to_dict()
        return jsonify({
            'success': True,
            'data': book_data,
            'message': 'Book created successfully'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/books/<uuid:book_id>', methods=['PUT'])
@staff_required
def update_book(book_id):
    """
    Update a book.
    
    Request body (all optional):
        title, author, isbn, publisher, year_published, description, category
    """
    service = get_book_service()
    data = request.get_json() or {}
    
    try:
        book = service.update_book(
            book_id=book_id,
            title=data.get('title'),
            author=data.get('author'),
            isbn=data.get('isbn'),
            publisher=data.get('publisher'),
            year_published=data.get('year_published'),
            description=data.get('description'),
            category=data.get('category')
        )
        
        book_data = BookSchema.from_model(book).to_dict()
        return api_success(data=book_data, message='Book updated successfully')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('Book', str(book_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/books/<uuid:book_id>', methods=['DELETE'])
@admin_required
def delete_book(book_id):
    """Deactivate a book (soft delete)."""
    service = get_book_service()
    
    try:
        service.deactivate_book(book_id)
        return jsonify({
            'success': True,
            'message': 'Book deactivated successfully'
        }), 200
        
    except NotFoundError as e:
        return api_not_found('Book', str(book_id))


@bp.route('/books/<uuid:book_id>/reactivate', methods=['POST'])
@admin_required
def reactivate_book(book_id):
    """Reactivate a deactivated book."""
    service = get_book_service()
    
    try:
        book = service.reactivate_book(book_id)
        book_data = BookSchema.from_model(book).to_dict()
        return api_success(data=book_data, message='Book reactivated successfully')
        
    except NotFoundError as e:
        return api_not_found('Book', str(book_id))


@bp.route('/books/isbn/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    """Get a book by ISBN."""
    service = get_book_service()
    
    book = service.get_by_isbn(isbn)
    if not book:
        return api_not_found('Book', f'ISBN: {isbn}')
    
    book_data = BookSchema.from_model(book, include_inventory_stats=True).to_dict()
    return api_success(data=book_data)


@bp.route('/books/categories', methods=['GET'])
def list_categories():
    """Get all book categories."""
    service = get_book_service()
    categories = service.get_categories()
    return api_success(data=categories)


@bp.route('/books/recent', methods=['GET'])
def get_recent_books():
    """Get recently added books."""
    service = get_book_service()
    limit = request.args.get('limit', 10, type=int)
    limit = min(limit, 50)
    
    books = service.get_recently_added(limit)
    books_data = [BookSchema.from_model(book).to_dict() for book in books]
    return api_success(data=books_data)
