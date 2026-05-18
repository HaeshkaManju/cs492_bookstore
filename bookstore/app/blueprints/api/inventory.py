"""
Inventory API Endpoints
=======================

REST API for inventory management.
Task: BE-S2-002
"""

from flask import request, jsonify
from uuid import UUID
from decimal import Decimal, InvalidOperation

from app.blueprints.api import bp
from app.blueprints.api.auth import jwt_required, staff_required, admin_required
from app.api import get_inventory_service, api_success, api_error, api_validation_error, api_not_found
from app.services.base import ValidationError, NotFoundError, ConflictError
from app.schemas import InventorySchema, WarehouseSchema


def _parse_decimal(value, default=None):
    """Safely parse decimal from request."""
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return default


@bp.route('/inventory', methods=['GET'])
def list_inventory():
    """
    List and search inventory.
    
    Query params:
        q: Search query (book title/author)
        warehouse_id: Filter by warehouse
        min_condition: Minimum condition (1-5)
        in_stock_only: Only items with quantity > 0
        page: Page number
        per_page: Items per page
    """
    service = get_inventory_service()
    
    query = request.args.get('q', '')
    warehouse_id = request.args.get('warehouse_id')
    min_condition = request.args.get('min_condition', type=int)
    in_stock_only = request.args.get('in_stock_only', 'true').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    warehouse_uuid = UUID(warehouse_id) if warehouse_id else None
    
    results = service.search(
        query=query,
        warehouse_id=warehouse_uuid,
        min_condition=min_condition,
        in_stock_only=in_stock_only,
        page=page,
        per_page=per_page
    )
    
    inventory_data = [InventorySchema.from_model(inv).to_dict() for inv in results['items']]
    
    return jsonify({
        'success': True,
        'data': inventory_data,
        'pagination': {
            'total': results['total'],
            'page': results['page'],
            'per_page': results['per_page'],
            'pages': results['pages']
        }
    }), 200


@bp.route('/inventory/<uuid:inventory_id>', methods=['GET'])
def get_inventory(inventory_id):
    """Get a single inventory item."""
    service = get_inventory_service()
    
    inventory = service.get_by_id(inventory_id)
    if not inventory:
        return api_not_found('Inventory', str(inventory_id))
    
    inventory_data = InventorySchema.from_model(inventory).to_dict()
    return api_success(data=inventory_data)


@bp.route('/inventory', methods=['POST'])
@staff_required
def add_inventory():
    """
    Add inventory for a book.
    
    Request body:
        book_id: Book UUID (required)
        warehouse_id: Warehouse UUID (required)
        condition: Condition grade 1-5 (required)
        quantity: Number of copies (required)
        acquisition_cost: Cost per item (required)
        list_price: Selling price (required)
        reorder_level: Low stock threshold (optional, default 1)
        location_code: Shelf location (optional)
    """
    service = get_inventory_service()
    data = request.get_json() or {}
    
    try:
        book_id = UUID(data.get('book_id', ''))
        warehouse_id = UUID(data.get('warehouse_id', ''))
    except (ValueError, TypeError):
        return api_validation_error(['Invalid book_id or warehouse_id format'])
    
    acquisition_cost = _parse_decimal(data.get('acquisition_cost'))
    list_price = _parse_decimal(data.get('list_price'))
    
    if acquisition_cost is None or list_price is None:
        return api_validation_error(['acquisition_cost and list_price are required'])
    
    try:
        inventory = service.add_inventory(
            book_id=book_id,
            warehouse_id=warehouse_id,
            condition=data.get('condition', 3),
            quantity=data.get('quantity', 1),
            acquisition_cost=acquisition_cost,
            list_price=list_price,
            reorder_level=data.get('reorder_level', 1),
            location_code=data.get('location_code')
        )
        
        inventory_data = InventorySchema.from_model(inventory).to_dict()
        return jsonify({
            'success': True,
            'data': inventory_data,
            'message': 'Inventory added successfully'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found(e.resource_type, str(e.resource_id))


@bp.route('/inventory/<uuid:inventory_id>', methods=['PUT'])
@staff_required
def update_inventory(inventory_id):
    """
    Update inventory pricing or reorder level.
    
    Request body (all optional):
        list_price, acquisition_cost, reorder_level, location_code
    """
    service = get_inventory_service()
    data = request.get_json() or {}
    
    try:
        inventory = service.get_by_id(inventory_id)
        if not inventory:
            return api_not_found('Inventory', str(inventory_id))
        
        if 'list_price' in data or 'acquisition_cost' in data:
            service.update_pricing(
                inventory_id=inventory_id,
                list_price=_parse_decimal(data.get('list_price')),
                acquisition_cost=_parse_decimal(data.get('acquisition_cost'))
            )
        
        if 'reorder_level' in data:
            service.update_reorder_level(
                inventory_id=inventory_id,
                reorder_level=data['reorder_level']
            )
        
        if 'location_code' in data:
            service.update_location(
                inventory_id=inventory_id,
                location_code=data['location_code']
            )
        
        inventory = service.get_by_id(inventory_id)
        inventory_data = InventorySchema.from_model(inventory).to_dict()
        return api_success(data=inventory_data, message='Inventory updated successfully')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('Inventory', str(inventory_id))


@bp.route('/inventory/<uuid:inventory_id>/adjust', methods=['POST'])
@staff_required
def adjust_inventory(inventory_id):
    """
    Adjust inventory quantity.
    
    Request body:
        delta: Amount to add (positive) or remove (negative)
        reason: Optional reason for adjustment
    """
    service = get_inventory_service()
    data = request.get_json() or {}
    
    delta = data.get('delta', 0)
    reason = data.get('reason')
    
    try:
        inventory = service.adjust_quantity(
            inventory_id=inventory_id,
            delta=delta,
            reason=reason
        )
        
        inventory_data = InventorySchema.from_model(inventory).to_dict()
        return api_success(data=inventory_data, message=f'Quantity adjusted by {delta}')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('Inventory', str(inventory_id))


@bp.route('/inventory/<uuid:inventory_id>/reserve', methods=['POST'])
@staff_required
def reserve_inventory(inventory_id):
    """
    Reserve inventory for a sale.
    
    Request body:
        quantity: Quantity to reserve
    """
    service = get_inventory_service()
    data = request.get_json() or {}
    
    quantity = data.get('quantity', 1)
    
    try:
        inventory = service.reserve_inventory(
            inventory_id=inventory_id,
            quantity=quantity
        )
        
        inventory_data = InventorySchema.from_model(inventory).to_dict()
        return api_success(data=inventory_data, message=f'Reserved {quantity} units')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('Inventory', str(inventory_id))


@bp.route('/inventory/book/<uuid:book_id>', methods=['GET'])
def get_inventory_by_book(book_id):
    """Get all inventory records for a book."""
    service = get_inventory_service()
    
    in_stock_only = request.args.get('in_stock_only', 'false').lower() == 'true'
    
    items = service.get_by_book(book_id, in_stock_only)
    inventory_data = [InventorySchema.from_model(inv).to_dict() for inv in items]
    return api_success(data=inventory_data)


@bp.route('/inventory/low-stock', methods=['GET'])
def get_low_stock():
    """Get items at or below reorder level."""
    service = get_inventory_service()
    
    warehouse_id = request.args.get('warehouse_id')
    warehouse_uuid = UUID(warehouse_id) if warehouse_id else None
    
    items = service.get_low_stock(warehouse_uuid)
    inventory_data = [InventorySchema.from_model(inv).to_dict() for inv in items]
    return api_success(data=inventory_data)


@bp.route('/inventory/out-of-stock', methods=['GET'])
def get_out_of_stock():
    """Get out-of-stock items."""
    service = get_inventory_service()
    
    warehouse_id = request.args.get('warehouse_id')
    warehouse_uuid = UUID(warehouse_id) if warehouse_id else None
    
    items = service.get_out_of_stock(warehouse_uuid)
    inventory_data = [InventorySchema.from_model(inv).to_dict() for inv in items]
    return api_success(data=inventory_data)


@bp.route('/inventory/value', methods=['GET'])
def get_inventory_value():
    """Get total inventory value."""
    service = get_inventory_service()
    
    warehouse_id = request.args.get('warehouse_id')
    warehouse_uuid = UUID(warehouse_id) if warehouse_id else None
    
    value = service.get_total_value(warehouse_uuid)
    return api_success(data={
        'acquisition_value': str(value.get('acquisition_value', 0)),
        'list_value': str(value.get('list_value', 0))
    })


# Warehouse endpoints

@bp.route('/warehouses', methods=['GET'])
def list_warehouses():
    """Get all warehouses."""
    service = get_inventory_service()
    
    warehouses = service.get_warehouses()
    warehouses_data = [WarehouseSchema.from_model(w).to_dict() for w in warehouses]
    return api_success(data=warehouses_data)


@bp.route('/warehouses', methods=['POST'])
@admin_required
def create_warehouse():
    """
    Create a new warehouse.
    
    Request body:
        name: Warehouse name (required)
        location: Address (optional)
        capacity: Item capacity (optional, default 10000)
    """
    service = get_inventory_service()
    data = request.get_json() or {}
    
    try:
        warehouse = service.create_warehouse(
            name=data.get('name', ''),
            location=data.get('location'),
            capacity=data.get('capacity', 10000)
        )
        
        warehouse_data = WarehouseSchema.from_model(warehouse).to_dict()
        return jsonify({
            'success': True,
            'data': warehouse_data,
            'message': 'Warehouse created successfully'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)


@bp.route('/warehouses/stats', methods=['GET'])
def get_warehouse_stats():
    """Get warehouses with inventory statistics."""
    service = get_inventory_service()
    stats = service.get_warehouse_stats()
    return api_success(data=stats)
