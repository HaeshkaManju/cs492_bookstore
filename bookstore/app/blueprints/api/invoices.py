"""
Invoices/Sales API Endpoints
============================

REST API for invoice and sales management.
Task: BE-S2-003
"""

from flask import request, jsonify
from uuid import UUID
from decimal import Decimal, InvalidOperation

from app.blueprints.api import bp
from app.blueprints.api.auth import jwt_required, staff_required, admin_required
from app.api import get_invoice_service, api_success, api_error, api_validation_error, api_not_found
from app.services.base import ValidationError, NotFoundError, ConflictError
from app.schemas import InvoiceSchema, InvoiceLineSchema


def _parse_decimal(value, default=None):
    """Safely parse decimal from request."""
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return default


@bp.route('/invoices', methods=['GET'])
@staff_required
def list_invoices():
    """
    List invoices with optional filtering.
    
    Query params:
        q: Search query (invoice number, customer name)
        status: Filter by status (draft, sent, paid, cancelled)
        customer_id: Filter by customer
        page: Page number
        per_page: Items per page
    """
    service = get_invoice_service()
    
    query = request.args.get('q', '')
    status = request.args.get('status')
    customer_id = request.args.get('customer_id')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    if customer_id:
        try:
            customer_uuid = UUID(customer_id)
            results = service.get_by_customer(customer_uuid, status, page, per_page)
        except ValueError:
            return api_validation_error(['Invalid customer_id format'])
    elif query:
        results = service.search(query, status, page, per_page)
    elif status:
        results = service.get_by_status(status, page, per_page)
    else:
        results = service.search('', None, page, per_page)
    
    invoices_data = [InvoiceSchema.from_model(inv).to_dict() for inv in results['items']]
    
    return jsonify({
        'success': True,
        'data': invoices_data,
        'pagination': {
            'total': results['total'],
            'page': results['page'],
            'per_page': results['per_page'],
            'pages': results['pages']
        }
    }), 200


@bp.route('/invoices/<uuid:invoice_id>', methods=['GET'])
@jwt_required
def get_invoice(invoice_id):
    """Get invoice with line items."""
    service = get_invoice_service()
    
    invoice = service.get_with_lines(invoice_id)
    if not invoice:
        return api_not_found('Invoice', str(invoice_id))
    
    invoice_data = InvoiceSchema.from_model(invoice, include_lines=True).to_dict()
    return api_success(data=invoice_data)


@bp.route('/invoices', methods=['POST'])
@staff_required
def create_invoice():
    """
    Create a new draft invoice.
    
    Request body:
        customer_id: Customer UUID (required)
        created_by: User UUID who created the invoice (required)
        payment_terms: Payment terms text (optional, default "Net 30")
        notes: Optional notes
    """
    service = get_invoice_service()
    data = request.get_json() or {}
    
    try:
        customer_id = UUID(data.get('customer_id', ''))
        created_by = UUID(data.get('created_by', ''))
    except (ValueError, TypeError):
        return api_validation_error(['Invalid customer_id or created_by format'])
    
    try:
        invoice = service.create_invoice(
            customer_id=customer_id,
            created_by=created_by,
            payment_terms=data.get('payment_terms', 'Net 30'),
            notes=data.get('notes')
        )
        
        invoice_data = InvoiceSchema.from_model(invoice).to_dict()
        return jsonify({
            'success': True,
            'data': invoice_data,
            'message': 'Invoice created successfully'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('Customer', str(data.get('customer_id')))


@bp.route('/invoices/<uuid:invoice_id>/lines', methods=['POST'])
@staff_required
def add_invoice_line(invoice_id):
    """
    Add a line item to invoice.
    
    Request body (one of):
        inventory_id: Inventory item to add (quantity optional, default 1)
        request_id: Book request to add as pending line
        
        OR for custom line:
        description: Line description
        quantity: Quantity
        unit_price: Price per unit
    """
    service = get_invoice_service()
    data = request.get_json() or {}
    
    try:
        if 'inventory_id' in data:
            inventory_id = UUID(data['inventory_id'])
            quantity = data.get('quantity', 1)
            
            line = service.add_inventory_line(
                invoice_id=invoice_id,
                inventory_id=inventory_id,
                quantity=quantity
            )
        elif 'request_id' in data:
            request_id = UUID(data['request_id'])
            
            line = service.add_request_line(
                invoice_id=invoice_id,
                request_id=request_id
            )
        elif 'description' in data:
            unit_price = _parse_decimal(data.get('unit_price'))
            if unit_price is None:
                return api_validation_error(['unit_price is required for custom lines'])
            
            line = service.add_custom_line(
                invoice_id=invoice_id,
                description=data['description'],
                quantity=data.get('quantity', 1),
                unit_price=unit_price
            )
        else:
            return api_validation_error(['Provide inventory_id, request_id, or description'])
        
        line_data = InvoiceLineSchema.from_model(line).to_dict()
        return jsonify({
            'success': True,
            'data': line_data,
            'message': 'Line added successfully'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found(e.resource_type, str(e.resource_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/invoices/<uuid:invoice_id>/lines/<uuid:line_id>', methods=['DELETE'])
@staff_required
def remove_invoice_line(invoice_id, line_id):
    """Remove a line item from invoice."""
    service = get_invoice_service()
    
    try:
        service.remove_line(line_id)
        return api_success(message='Line removed successfully')
        
    except NotFoundError as e:
        return api_not_found('InvoiceLine', str(line_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/invoices/<uuid:invoice_id>/send', methods=['POST'])
@staff_required
def send_invoice(invoice_id):
    """Send invoice (change status from draft to sent)."""
    service = get_invoice_service()
    
    try:
        invoice = service.send_invoice(invoice_id)
        invoice_data = InvoiceSchema.from_model(invoice).to_dict()
        return api_success(data=invoice_data, message='Invoice sent successfully')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('Invoice', str(invoice_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/invoices/<uuid:invoice_id>/pay', methods=['POST'])
@staff_required
def mark_invoice_paid(invoice_id):
    """Mark invoice as paid."""
    service = get_invoice_service()
    
    try:
        invoice = service.mark_paid(invoice_id)
        invoice_data = InvoiceSchema.from_model(invoice).to_dict()
        return api_success(data=invoice_data, message='Invoice marked as paid')
        
    except NotFoundError as e:
        return api_not_found('Invoice', str(invoice_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/invoices/<uuid:invoice_id>/cancel', methods=['POST'])
@admin_required
def cancel_invoice(invoice_id):
    """Cancel invoice."""
    service = get_invoice_service()
    
    try:
        invoice = service.cancel_invoice(invoice_id)
        invoice_data = InvoiceSchema.from_model(invoice).to_dict()
        return api_success(data=invoice_data, message='Invoice cancelled')
        
    except NotFoundError as e:
        return api_not_found('Invoice', str(invoice_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/invoices/number/<invoice_number>', methods=['GET'])
def get_invoice_by_number(invoice_number):
    """Get invoice by invoice number."""
    service = get_invoice_service()
    
    invoice = service.get_by_number(invoice_number)
    if not invoice:
        return api_not_found('Invoice', invoice_number)
    
    invoice_data = InvoiceSchema.from_model(invoice, include_lines=True).to_dict()
    return api_success(data=invoice_data)


@bp.route('/invoices/overdue', methods=['GET'])
def get_overdue_invoices():
    """Get overdue invoices."""
    service = get_invoice_service()
    
    payment_days = request.args.get('payment_days', 30, type=int)
    
    invoices = service.get_overdue(payment_days)
    invoices_data = [InvoiceSchema.from_model(inv).to_dict() for inv in invoices]
    return api_success(data=invoices_data)


@bp.route('/invoices/unpaid', methods=['GET'])
def get_unpaid_invoices():
    """Get unpaid invoices."""
    service = get_invoice_service()
    
    days_old = request.args.get('days_old', type=int)
    
    invoices = service.get_unpaid(days_old)
    invoices_data = [InvoiceSchema.from_model(inv).to_dict() for inv in invoices]
    return api_success(data=invoices_data)


@bp.route('/invoices/stats', methods=['GET'])
def get_invoice_stats():
    """Get invoice statistics by status."""
    service = get_invoice_service()
    
    stats = service.get_totals_by_status()
    return api_success(data=stats)
