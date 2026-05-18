"""
Purchase Orders API Endpoints
=============================

REST API for purchase order management.
Task: BE-S2-004
"""

from flask import request, jsonify
from uuid import UUID
from decimal import Decimal, InvalidOperation

from app.blueprints.api import bp
from app.blueprints.api.auth import jwt_required, staff_required, admin_required
from app.api import get_purchase_order_service, api_success, api_error, api_validation_error, api_not_found
from app.services.base import ValidationError, NotFoundError, ConflictError
from app.schemas import PurchaseOrderSchema, POLineSchema, ManufacturerSchema


def _parse_decimal(value, default=None):
    """Safely parse decimal from request."""
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return default


@bp.route('/purchase-orders', methods=['GET'])
@staff_required
def list_purchase_orders():
    """
    List purchase orders with optional filtering.
    
    Query params:
        q: Search query (PO number, manufacturer name)
        status: Filter by status (draft, submitted, confirmed, shipped, received, cancelled)
        manufacturer_id: Filter by manufacturer
        page: Page number
        per_page: Items per page
    """
    service = get_purchase_order_service()
    
    query = request.args.get('q', '')
    status = request.args.get('status')
    manufacturer_id = request.args.get('manufacturer_id')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    if manufacturer_id:
        try:
            manufacturer_uuid = UUID(manufacturer_id)
            results = service.get_by_manufacturer(manufacturer_uuid, status, page, per_page)
        except ValueError:
            return api_validation_error(['Invalid manufacturer_id format'])
    elif query:
        results = service.search(query, status, page, per_page)
    elif status:
        results = service.get_by_status(status, page, per_page)
    else:
        results = service.search('', None, page, per_page)
    
    pos_data = [PurchaseOrderSchema.from_model(po).to_dict() for po in results['items']]
    
    return jsonify({
        'success': True,
        'data': pos_data,
        'pagination': {
            'total': results['total'],
            'page': results['page'],
            'per_page': results['per_page'],
            'pages': results['pages']
        }
    }), 200


@bp.route('/purchase-orders/<uuid:po_id>', methods=['GET'])
@staff_required
def get_purchase_order(po_id):
    """Get purchase order with line items."""
    service = get_purchase_order_service()
    
    po = service.get_with_lines(po_id)
    if not po:
        return api_not_found('PurchaseOrder', str(po_id))
    
    po_data = PurchaseOrderSchema.from_model(po, include_lines=True).to_dict()
    return api_success(data=po_data)


@bp.route('/purchase-orders', methods=['POST'])
@staff_required
def create_purchase_order():
    """
    Create a new draft purchase order.
    
    Request body:
        manufacturer_id: Manufacturer UUID (required)
        created_by: User UUID who created the PO (required)
        notes: Optional notes
    """
    service = get_purchase_order_service()
    data = request.get_json() or {}
    
    try:
        manufacturer_id = UUID(data.get('manufacturer_id', ''))
        created_by = UUID(data.get('created_by', ''))
    except (ValueError, TypeError):
        return api_validation_error(['Invalid manufacturer_id or created_by format'])
    
    try:
        po = service.create_purchase_order(
            manufacturer_id=manufacturer_id,
            created_by=created_by,
            notes=data.get('notes')
        )
        
        po_data = PurchaseOrderSchema.from_model(po).to_dict()
        return jsonify({
            'success': True,
            'data': po_data,
            'message': 'Purchase order created successfully'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('Manufacturer', str(data.get('manufacturer_id')))


@bp.route('/purchase-orders/<uuid:po_id>/lines', methods=['POST'])
def add_po_line(po_id):
    """
    Add a line item to purchase order.
    
    Request body:
        description: Item description (required)
        quantity: Quantity to order (required)
        unit_cost: Cost per item (required)
        book_id: Optional book reference
        isbn: Optional ISBN
        expected_condition: Expected condition grade (1-5)
    """
    service = get_purchase_order_service()
    data = request.get_json() or {}
    
    unit_cost = _parse_decimal(data.get('unit_cost'))
    if unit_cost is None:
        return api_validation_error(['unit_cost is required'])
    
    book_id = None
    if data.get('book_id'):
        try:
            book_id = UUID(data['book_id'])
        except ValueError:
            return api_validation_error(['Invalid book_id format'])
    
    try:
        line = service.add_line(
            po_id=po_id,
            description=data.get('description', ''),
            quantity=data.get('quantity', 1),
            unit_cost=unit_cost,
            book_id=book_id,
            isbn=data.get('isbn'),
            expected_condition=data.get('expected_condition')
        )
        
        line_data = POLineSchema.from_model(line).to_dict()
        return jsonify({
            'success': True,
            'data': line_data,
            'message': 'Line added successfully'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('PurchaseOrder', str(po_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/purchase-orders/<uuid:po_id>/lines/<uuid:line_id>', methods=['DELETE'])
def remove_po_line(po_id, line_id):
    """Remove a line item from purchase order."""
    service = get_purchase_order_service()
    
    try:
        service.remove_line(line_id)
        return api_success(message='Line removed successfully')
        
    except NotFoundError as e:
        return api_not_found('POLine', str(line_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/purchase-orders/<uuid:po_id>/submit', methods=['POST'])
@admin_required
def submit_po(po_id):
    """Submit purchase order to manufacturer."""
    service = get_purchase_order_service()
    
    try:
        po = service.submit_po(po_id)
        po_data = PurchaseOrderSchema.from_model(po).to_dict()
        return api_success(data=po_data, message='Purchase order submitted')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('PurchaseOrder', str(po_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/purchase-orders/<uuid:po_id>/confirm', methods=['POST'])
def confirm_po(po_id):
    """Confirm purchase order (manufacturer acknowledged)."""
    service = get_purchase_order_service()
    
    try:
        po = service.confirm_po(po_id)
        po_data = PurchaseOrderSchema.from_model(po).to_dict()
        return api_success(data=po_data, message='Purchase order confirmed')
        
    except NotFoundError as e:
        return api_not_found('PurchaseOrder', str(po_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/purchase-orders/<uuid:po_id>/ship', methods=['POST'])
def mark_po_shipped(po_id):
    """Mark purchase order as shipped."""
    service = get_purchase_order_service()
    
    try:
        po = service.mark_shipped(po_id)
        po_data = PurchaseOrderSchema.from_model(po).to_dict()
        return api_success(data=po_data, message='Purchase order marked as shipped')
        
    except NotFoundError as e:
        return api_not_found('PurchaseOrder', str(po_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/purchase-orders/<uuid:po_id>/lines/<uuid:line_id>/receive', methods=['POST'])
def receive_po_line(po_id, line_id):
    """
    Record receipt of items for a PO line.
    
    Request body:
        received_quantity: Number of items received
    """
    service = get_purchase_order_service()
    data = request.get_json() or {}
    
    received_qty = data.get('received_quantity', 0)
    
    try:
        line = service.receive_line(line_id, received_qty)
        line_data = POLineSchema.from_model(line).to_dict()
        return api_success(data=line_data, message=f'Received {received_qty} items')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('POLine', str(line_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/purchase-orders/<uuid:po_id>/receive', methods=['POST'])
def receive_po(po_id):
    """Mark entire purchase order as received."""
    service = get_purchase_order_service()
    
    try:
        po = service.receive_po(po_id)
        po_data = PurchaseOrderSchema.from_model(po).to_dict()
        return api_success(data=po_data, message='Purchase order received')
        
    except NotFoundError as e:
        return api_not_found('PurchaseOrder', str(po_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/purchase-orders/<uuid:po_id>/cancel', methods=['POST'])
def cancel_po(po_id):
    """Cancel purchase order."""
    service = get_purchase_order_service()
    
    try:
        po = service.cancel_po(po_id)
        po_data = PurchaseOrderSchema.from_model(po).to_dict()
        return api_success(data=po_data, message='Purchase order cancelled')
        
    except NotFoundError as e:
        return api_not_found('PurchaseOrder', str(po_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/purchase-orders/number/<po_number>', methods=['GET'])
def get_po_by_number(po_number):
    """Get purchase order by PO number."""
    service = get_purchase_order_service()
    
    po = service.get_by_number(po_number)
    if not po:
        return api_not_found('PurchaseOrder', po_number)
    
    po_data = PurchaseOrderSchema.from_model(po, include_lines=True).to_dict()
    return api_success(data=po_data)


@bp.route('/purchase-orders/awaiting-receipt', methods=['GET'])
def get_awaiting_receipt():
    """Get POs awaiting receipt (shipped status)."""
    service = get_purchase_order_service()
    
    pos = service.get_awaiting_receipt()
    pos_data = [PurchaseOrderSchema.from_model(po).to_dict() for po in pos]
    return api_success(data=pos_data)


@bp.route('/purchase-orders/drafts', methods=['GET'])
def get_draft_pos():
    """Get draft purchase orders."""
    service = get_purchase_order_service()
    
    created_by = request.args.get('created_by')
    created_by_uuid = UUID(created_by) if created_by else None
    
    pos = service.get_drafts(created_by_uuid)
    pos_data = [PurchaseOrderSchema.from_model(po).to_dict() for po in pos]
    return api_success(data=pos_data)


@bp.route('/purchase-orders/stats', methods=['GET'])
def get_po_stats():
    """Get purchase order statistics by status."""
    service = get_purchase_order_service()
    
    stats = service.get_totals_by_status()
    return api_success(data=stats)


# Manufacturer endpoints

@bp.route('/manufacturers', methods=['GET'])
def list_manufacturers():
    """Get all manufacturers."""
    service = get_purchase_order_service()
    
    query = request.args.get('q')
    
    if query:
        manufacturers = service.search_manufacturers(query)
    else:
        manufacturers = service.get_manufacturers()
    
    manufacturers_data = [ManufacturerSchema.from_model(m).to_dict() for m in manufacturers]
    return api_success(data=manufacturers_data)


@bp.route('/manufacturers', methods=['POST'])
def create_manufacturer():
    """
    Create a new manufacturer.
    
    Request body:
        name: Manufacturer name (required)
        contact_name: Primary contact (optional)
        email: Contact email (optional)
        phone: Contact phone (optional)
        address: Mailing address (optional)
    """
    service = get_purchase_order_service()
    data = request.get_json() or {}
    
    try:
        manufacturer = service.create_manufacturer(
            name=data.get('name', ''),
            contact_name=data.get('contact_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address')
        )
        
        manufacturer_data = ManufacturerSchema.from_model(manufacturer).to_dict()
        return jsonify({
            'success': True,
            'data': manufacturer_data,
            'message': 'Manufacturer created successfully'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)
