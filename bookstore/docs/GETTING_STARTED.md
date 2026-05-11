# Getting Started - Step by Step Tutorial

## For Complete Beginners

---

This tutorial will walk you through building your first feature using the Bookstore API. By the end, you will have:

1. Created a Flask route
2. Used a service to perform business logic
3. Handled errors properly
4. Returned a JSON response

**Prerequisites**: Python 3.9+, basic Python knowledge, pip installed

---

## Part 1: Understanding Flask Basics

### What is Flask?

Flask is a **web framework** for Python. It lets you create web applications that respond to HTTP requests (like when you visit a URL in your browser).

### How Flask Works

When someone visits a URL like `http://localhost:5000/books`, Flask:

1. Receives the HTTP request
2. Looks for a function that handles that URL
3. Runs that function
4. Sends the function's return value as the response

```
User visits URL  →  Flask finds handler  →  Handler function runs  →  Response sent
```

### The Simplest Flask App

```python
from flask import Flask

# Create the Flask application
app = Flask(__name__)

# Define a route (URL handler)
@app.route('/hello')
def hello():
    return "Hello, World!"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
```

When you run this and visit `http://localhost:5000/hello`, you see "Hello, World!".

---

## Part 2: Setting Up the Project

### Step 1: Navigate to the Project

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux).

```bash
cd path/to/bookstore
```

### Step 2: Create a Virtual Environment

A virtual environment keeps your Python packages separate from other projects.

```bash
# Create the virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# You should see (venv) at the start of your terminal prompt
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up the Database

```bash
# Create environment file
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux

# Initialize database
flask db upgrade
```

### Step 5: Verify Everything Works

```bash
flask shell
```

In the Flask shell, type:

```python
>>> from app.models import Book
>>> print("Setup successful!")
>>> exit()
```

---

## Part 3: Creating Your First Feature

Let's create a simple feature: **List all books**.

### Step 1: Understand the Goal

We want to create an endpoint that:
- URL: `GET /api/books`
- Returns: JSON list of all books
- Includes: pagination (not all books at once)

### Step 2: Create the Route File

Create a new file: `app/routes/books.py`

```python
"""
Book Routes
===========

This file contains all the URL handlers (routes) for book-related operations.

Each function decorated with @blueprint.route() handles a specific URL.
"""

from flask import Blueprint, request, jsonify
from uuid import UUID

# Import our service and helpers
from app.api import get_book_service, api_success, api_error, api_not_found
from app.schemas import BookSchema
from app.services.base import ValidationError, NotFoundError

# Create a Blueprint (a group of routes)
# The first argument is the name, used for internal references
# The second argument is the module name (use __name__)
blueprint = Blueprint('books', __name__)


@blueprint.route('/api/books', methods=['GET'])
def list_books():
    """
    List all books with pagination.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
        - category: Filter by category (optional)
        - in_stock: Only show in-stock books (optional)
    
    Returns:
        JSON with:
        - items: List of book objects
        - total: Total number of books
        - page: Current page
        - pages: Total pages
    """
    # Step 1: Get query parameters from the URL
    # Example: /api/books?page=2&per_page=10
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category', None)
    in_stock = request.args.get('in_stock', 'false').lower() == 'true'
    
    # Step 2: Validate the parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20
    
    # Step 3: Get the service
    book_service = get_book_service()
    
    # Step 4: Call the service method
    results = book_service.search(
        query='',  # Empty query = all books
        category=category,
        in_stock_only=in_stock,
        page=page,
        per_page=per_page
    )
    
    # Step 5: Convert models to schemas (safe for JSON)
    book_dicts = [
        BookSchema.from_model(book, include_inventory_stats=True).to_dict()
        for book in results['items']
    ]
    
    # Step 6: Return the response
    return api_success(data={
        'items': book_dicts,
        'total': results['total'],
        'page': results['page'],
        'pages': results['pages'],
        'per_page': results['per_page']
    })


@blueprint.route('/api/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """
    Get a single book by ID.
    
    URL Parameters:
        - book_id: The UUID of the book
    
    Returns:
        JSON with the book object, or 404 if not found.
    """
    try:
        # Step 1: Convert string ID to UUID
        # This will raise ValueError if the ID is not a valid UUID
        book_uuid = UUID(book_id)
        
        # Step 2: Get the service
        book_service = get_book_service()
        
        # Step 3: Try to get the book
        book = book_service.get_by_id(book_uuid)
        
        # Step 4: Convert to schema and return
        book_dict = BookSchema.from_model(book, include_inventory_stats=True).to_dict()
        return api_success(data=book_dict)
        
    except ValueError:
        # Invalid UUID format
        return api_error('Invalid book ID format', code='INVALID_ID', status=400)
        
    except NotFoundError:
        # Book doesn't exist
        return api_not_found('Book', book_id)
        
    except Exception as e:
        # Unexpected error
        return api_error(str(e), code='INTERNAL_ERROR', status=500)


@blueprint.route('/api/books', methods=['POST'])
def create_book():
    """
    Create a new book.
    
    Request Body (JSON):
        - title: Book title (required)
        - author: Author name (required)
        - isbn: ISBN-10 or ISBN-13 (optional)
        - publisher: Publisher name (optional)
        - year_published: Year (optional)
        - description: Book description (optional)
        - category: Category name (optional)
    
    Returns:
        JSON with the created book, or validation errors.
    """
    try:
        # Step 1: Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return api_error('Request body is required', code='NO_DATA', status=400)
        
        # Step 2: Get the service
        book_service = get_book_service()
        
        # Step 3: Create the book
        # The service will validate the data and raise ValidationError if invalid
        book = book_service.create_book(
            title=data.get('title'),
            author=data.get('author'),
            isbn=data.get('isbn'),
            publisher=data.get('publisher'),
            year_published=data.get('year_published'),
            description=data.get('description'),
            category=data.get('category')
        )
        
        # Step 4: Return success response
        book_dict = BookSchema.from_model(book).to_dict()
        return api_success(
            data=book_dict,
            message='Book created successfully',
            status=201  # 201 = Created
        )
        
    except ValidationError as e:
        # Validation failed - return the error messages
        return api_validation_error(e.errors)
        
    except Exception as e:
        return api_error(str(e), code='INTERNAL_ERROR', status=500)


@blueprint.route('/api/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Update an existing book.
    
    URL Parameters:
        - book_id: The UUID of the book
    
    Request Body (JSON):
        - Any fields to update (all optional)
    
    Returns:
        JSON with the updated book, or errors.
    """
    try:
        book_uuid = UUID(book_id)
        data = request.get_json()
        
        if not data:
            return api_error('Request body is required', code='NO_DATA', status=400)
        
        book_service = get_book_service()
        
        # Update only the fields that were provided
        book = book_service.update_book(
            book_id=book_uuid,
            title=data.get('title'),
            author=data.get('author'),
            isbn=data.get('isbn'),
            publisher=data.get('publisher'),
            year_published=data.get('year_published'),
            description=data.get('description'),
            category=data.get('category')
        )
        
        book_dict = BookSchema.from_model(book).to_dict()
        return api_success(data=book_dict, message='Book updated successfully')
        
    except ValueError:
        return api_error('Invalid book ID format', code='INVALID_ID', status=400)
    except NotFoundError:
        return api_not_found('Book', book_id)
    except ValidationError as e:
        return api_validation_error(e.errors)
    except Exception as e:
        return api_error(str(e), code='INTERNAL_ERROR', status=500)


@blueprint.route('/api/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Delete (deactivate) a book.
    
    This performs a "soft delete" - the book is marked as inactive
    but not actually removed from the database.
    
    URL Parameters:
        - book_id: The UUID of the book
    
    Returns:
        Success message or error.
    """
    try:
        book_uuid = UUID(book_id)
        book_service = get_book_service()
        
        # Soft delete
        book_service.deactivate_book(book_uuid)
        
        return api_success(message='Book deactivated successfully')
        
    except ValueError:
        return api_error('Invalid book ID format', code='INVALID_ID', status=400)
    except NotFoundError:
        return api_not_found('Book', book_id)
    except Exception as e:
        return api_error(str(e), code='INTERNAL_ERROR', status=500)


@blueprint.route('/api/books/search', methods=['GET'])
def search_books():
    """
    Search books by title, author, or ISBN.
    
    Query Parameters:
        - q: Search query (required)
        - category: Filter by category (optional)
        - in_stock: Only show in-stock books (optional)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
    
    Returns:
        JSON with search results.
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return api_error('Search query is required', code='MISSING_QUERY', status=400)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category', None)
    in_stock = request.args.get('in_stock', 'false').lower() == 'true'
    
    book_service = get_book_service()
    
    results = book_service.search(
        query=query,
        category=category,
        in_stock_only=in_stock,
        page=page,
        per_page=per_page
    )
    
    book_dicts = [
        BookSchema.from_model(book, include_inventory_stats=True).to_dict()
        for book in results['items']
    ]
    
    return api_success(data={
        'query': query,
        'items': book_dicts,
        'total': results['total'],
        'page': results['page'],
        'pages': results['pages']
    })
```

### Step 3: Register the Blueprint

Open `app/__init__.py` and add:

```python
def create_app(config_name='development'):
    app = Flask(__name__)
    # ... existing code ...
    
    # Register blueprints (route groups)
    from app.routes import books
    app.register_blueprint(books.blueprint)
    
    return app
```

### Step 4: Test Your Routes

Start the application:

```bash
flask run
```

Open another terminal and test with curl (or use Postman):

```bash
# List all books
curl http://localhost:5000/api/books

# Search for books
curl "http://localhost:5000/api/books/search?q=python"

# Create a book
curl -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Book", "author": "Test Author"}'
```

---

## Part 4: Understanding the Code

Let's break down what's happening in each part:

### Imports Explained

```python
from flask import Blueprint, request, jsonify
```

- `Blueprint`: Groups related routes together
- `request`: Gives you access to the incoming HTTP request
- `jsonify`: Converts Python objects to JSON responses

```python
from app.api import get_book_service, api_success, api_error, api_not_found
```

- `get_book_service`: Factory function that returns a BookService instance
- `api_success`: Helper to create success responses
- `api_error`: Helper to create error responses
- `api_not_found`: Helper to create 404 responses

```python
from app.schemas import BookSchema
```

- `BookSchema`: Data transfer object that defines what book data looks like in responses

```python
from app.services.base import ValidationError, NotFoundError
```

- `ValidationError`: Raised when input validation fails
- `NotFoundError`: Raised when a resource isn't found

### Route Decorators Explained

```python
@blueprint.route('/api/books', methods=['GET'])
def list_books():
```

- `@blueprint.route()`: Registers this function as a URL handler
- `'/api/books'`: The URL path this function handles
- `methods=['GET']`: This function only handles GET requests
- `def list_books()`: The function that runs when the URL is visited

### Getting URL Parameters

```python
# Query parameters (after the ?)
# URL: /api/books?page=2&per_page=10
page = request.args.get('page', 1, type=int)
# - 'page': The parameter name
# - 1: Default value if not provided
# - type=int: Convert to integer

# URL path parameters (in the URL)
# URL: /api/books/abc-123
@blueprint.route('/api/books/<book_id>')
def get_book(book_id):
    # book_id is automatically passed as an argument
```

### Getting Request Body

```python
# For POST/PUT requests with JSON body
data = request.get_json()

# Access fields
title = data.get('title')  # Returns None if not present
author = data['author']    # Raises KeyError if not present
```

### Error Handling Pattern

```python
try:
    # Your code here
    result = some_operation()
    return api_success(data=result)
    
except ValidationError as e:
    # Input was invalid
    return api_validation_error(e.errors)
    
except NotFoundError:
    # Resource not found
    return api_not_found('Resource', id)
    
except Exception as e:
    # Unexpected error
    return api_error(str(e), status=500)
```

---

## Part 5: Adding More Routes

Now that you understand the pattern, add these routes yourself:

### Exercise 1: Inventory Routes

Create `app/routes/inventory.py` with:

1. `GET /api/inventory` - List all inventory
2. `GET /api/inventory/<id>` - Get single inventory item
3. `POST /api/inventory` - Add inventory
4. `PUT /api/inventory/<id>` - Update inventory
5. `DELETE /api/inventory/<id>` - Remove inventory

### Exercise 2: Customer Routes

Create `app/routes/customers.py` with:

1. `GET /api/customers` - List customers
2. `GET /api/customers/<id>` - Get customer
3. `POST /api/customers` - Create customer
4. `PUT /api/customers/<id>` - Update customer
5. `POST /api/customers/<id>/addresses` - Add address

---

## Part 6: Testing Your Routes

### Manual Testing with curl

```bash
# GET request
curl http://localhost:5000/api/books

# GET with query params
curl "http://localhost:5000/api/books?page=1&per_page=10"

# POST with JSON body
curl -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "New Book", "author": "Author Name"}'

# PUT (update)
curl -X PUT http://localhost:5000/api/books/uuid-here \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# DELETE
curl -X DELETE http://localhost:5000/api/books/uuid-here
```

### Automated Testing with pytest

Create `tests/test_routes.py`:

```python
"""Tests for book routes."""

import pytest
import json

class TestBookRoutes:
    """Test the book API routes."""
    
    def test_list_books_empty(self, client):
        """Test listing books when database is empty."""
        response = client.get('/api/books')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['items'] == []
        assert data['data']['total'] == 0
    
    def test_list_books_with_data(self, client, sample_book):
        """Test listing books with data in database."""
        response = client.get('/api/books')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']['items']) == 1
        assert data['data']['items'][0]['title'] == sample_book.title
    
    def test_create_book_success(self, client):
        """Test creating a book with valid data."""
        response = client.post(
            '/api/books',
            data=json.dumps({
                'title': 'Test Book',
                'author': 'Test Author'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['title'] == 'Test Book'
    
    def test_create_book_missing_title(self, client):
        """Test that creating a book without title fails."""
        response = client.post(
            '/api/books',
            data=json.dumps({
                'author': 'Test Author'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_get_book_not_found(self, client):
        """Test getting a book that doesn't exist."""
        response = client.get('/api/books/00000000-0000-0000-0000-000000000000')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
```

Run the tests:

```bash
pytest tests/test_routes.py -v
```

---

## Congratulations!

You've learned:

1. How Flask routes work
2. How to use services for business logic
3. How to handle errors properly
4. How to test your code

**Next Steps:**

1. Read the [API Integration Guide](API_INTEGRATION_GUIDE.md) for complete service documentation
2. Study the existing service code in `app/services/`
3. Practice by implementing the exercises above
4. Ask questions when you get stuck!

Happy coding!
