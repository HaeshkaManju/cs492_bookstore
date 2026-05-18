"""
Users and Customers API Endpoints
=================================

REST API for user and customer management.
Task: BE-S2-005
"""

from flask import request, jsonify
from uuid import UUID

from app.blueprints.api import bp
from app.blueprints.api.auth import jwt_required, staff_required, admin_required
from app.api import get_user_service, get_customer_service, api_success, api_error, api_validation_error, api_not_found
from app.services.base import ValidationError, NotFoundError, ConflictError
from app.schemas import UserSchema, CustomerSchema, AddressSchema


# =============================================================================
# User Endpoints (Admin)
# =============================================================================

@bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """
    List users with optional filtering.
    
    Query params:
        q: Search query (name, email)
        role: Filter by role (admin, employee, customer)
        active_only: Only active users (default true)
    """
    service = get_user_service()
    
    query = request.args.get('q', '')
    role = request.args.get('role')
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    if query:
        users = service.search_users(query, role, active_only)
    elif role:
        users = service.get_by_role(role, active_only)
    else:
        users = service.search_users('', None, active_only)
    
    users_data = [UserSchema.from_model(u).to_dict() for u in users]
    return api_success(data=users_data)


@bp.route('/users/<uuid:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get a single user."""
    service = get_user_service()
    
    user = service.get_by_id(user_id)
    if not user:
        return api_not_found('User', str(user_id))
    
    user_data = UserSchema.from_model(user).to_dict()
    return api_success(data=user_data)


@bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """
    Create a new user (admin function).
    
    Request body:
        email: User email (required)
        password: Password (required)
        first_name: First name (required)
        last_name: Last name (required)
        role: User role (admin, employee, customer) - default customer
    """
    service = get_user_service()
    data = request.get_json() or {}
    
    try:
        user = service.create_user(
            email=data.get('email', ''),
            password=data.get('password', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data.get('role', 'customer')
        )
        
        user_data = UserSchema.from_model(user).to_dict()
        return jsonify({
            'success': True,
            'data': user_data,
            'message': 'User created successfully'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/users/<uuid:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update user profile.
    
    Request body (all optional):
        first_name, last_name
    """
    service = get_user_service()
    data = request.get_json() or {}
    
    try:
        user = service.update_profile(
            user_id=user_id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        user_data = UserSchema.from_model(user).to_dict()
        return api_success(data=user_data, message='User updated successfully')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('User', str(user_id))


@bp.route('/users/<uuid:user_id>/email', methods=['PUT'])
def update_user_email(user_id):
    """
    Update user email.
    
    Request body:
        email: New email address
    """
    service = get_user_service()
    data = request.get_json() or {}
    
    try:
        user = service.update_email(
            user_id=user_id,
            new_email=data.get('email', '')
        )
        
        user_data = UserSchema.from_model(user).to_dict()
        return api_success(data=user_data, message='Email updated successfully')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('User', str(user_id))
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/users/<uuid:user_id>/password', methods=['PUT'])
def change_user_password(user_id):
    """
    Change user password.
    
    Request body:
        current_password: Current password
        new_password: New password
    """
    service = get_user_service()
    data = request.get_json() or {}
    
    try:
        service.change_password(
            user_id=user_id,
            current_password=data.get('current_password', ''),
            new_password=data.get('new_password', '')
        )
        
        return api_success(message='Password changed successfully')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('User', str(user_id))


@bp.route('/users/<uuid:user_id>/role', methods=['PUT'])
def change_user_role(user_id):
    """
    Change user role (admin only).
    
    Request body:
        role: New role (admin, employee, customer)
    """
    service = get_user_service()
    data = request.get_json() or {}
    
    try:
        user = service.change_role(
            user_id=user_id,
            new_role=data.get('role', '')
        )
        
        user_data = UserSchema.from_model(user).to_dict()
        return api_success(data=user_data, message='Role updated successfully')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('User', str(user_id))


@bp.route('/users/<uuid:user_id>', methods=['DELETE'])
def deactivate_user(user_id):
    """Deactivate a user (soft delete)."""
    service = get_user_service()
    
    try:
        service.deactivate_user(user_id)
        return api_success(message='User deactivated successfully')
        
    except NotFoundError as e:
        return api_not_found('User', str(user_id))


@bp.route('/users/<uuid:user_id>/reactivate', methods=['POST'])
def reactivate_user(user_id):
    """Reactivate a deactivated user."""
    service = get_user_service()
    
    try:
        user = service.reactivate_user(user_id)
        user_data = UserSchema.from_model(user).to_dict()
        return api_success(data=user_data, message='User reactivated successfully')
        
    except NotFoundError as e:
        return api_not_found('User', str(user_id))


@bp.route('/users/staff', methods=['GET'])
def list_staff():
    """Get all staff users (admin and employee)."""
    service = get_user_service()
    
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    staff = service.get_staff(active_only)
    staff_data = [UserSchema.from_model(u).to_dict() for u in staff]
    return api_success(data=staff_data)


# =============================================================================
# Customer Endpoints
# =============================================================================

@bp.route('/customers', methods=['GET'])
@staff_required
def list_customers():
    """
    List customers with optional filtering.
    
    Query params:
        q: Search query (name, company, email)
        active_only: Only active customers (default true)
    """
    service = get_customer_service()
    
    query = request.args.get('q', '')
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    customers = service.search_customers(query, active_only)
    customers_data = [CustomerSchema.from_model(c).to_dict() for c in customers]
    return api_success(data=customers_data)


@bp.route('/customers/<uuid:customer_id>', methods=['GET'])
@jwt_required
def get_customer(customer_id):
    """Get a single customer with addresses."""
    service = get_customer_service()
    
    customer = service.get_by_id(customer_id)
    if not customer:
        return api_not_found('Customer', str(customer_id))
    
    customer_data = CustomerSchema.from_model(customer, include_addresses=True).to_dict()
    return api_success(data=customer_data)


@bp.route('/customers', methods=['POST'])
def create_customer():
    """
    Register a new customer (creates user + customer profile).
    
    Request body:
        email: Customer email (required)
        password: Account password (required)
        first_name: First name (required)
        last_name: Last name (required)
        company_name: Company name (optional)
        phone: Phone number (optional)
        credit_terms: Payment terms (optional, default "Net 30")
    """
    service = get_customer_service()
    data = request.get_json() or {}
    
    try:
        customer = service.create_customer(
            email=data.get('email', ''),
            password=data.get('password', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            company_name=data.get('company_name'),
            phone=data.get('phone'),
            credit_terms=data.get('credit_terms', 'Net 30')
        )
        
        customer_data = CustomerSchema.from_model(customer).to_dict()
        return jsonify({
            'success': True,
            'data': customer_data,
            'message': 'Customer registered successfully'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/customers/<uuid:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """
    Update customer profile.
    
    Request body (all optional):
        company_name, phone, notes, credit_terms
    """
    service = get_customer_service()
    data = request.get_json() or {}
    
    try:
        customer = service.update_customer(
            customer_id=customer_id,
            company_name=data.get('company_name'),
            phone=data.get('phone'),
            notes=data.get('notes'),
            credit_terms=data.get('credit_terms')
        )
        
        customer_data = CustomerSchema.from_model(customer).to_dict()
        return api_success(data=customer_data, message='Customer updated successfully')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('Customer', str(customer_id))


@bp.route('/customers/with-pending-requests', methods=['GET'])
def get_customers_with_pending_requests():
    """Get customers with pending book requests."""
    service = get_customer_service()
    
    customers = service.get_with_pending_requests()
    customers_data = [CustomerSchema.from_model(c).to_dict() for c in customers]
    return api_success(data=customers_data)


@bp.route('/customers/with-unpaid-invoices', methods=['GET'])
def get_customers_with_unpaid_invoices():
    """Get customers with unpaid invoices."""
    service = get_customer_service()
    
    customers = service.get_with_unpaid_invoices()
    customers_data = [CustomerSchema.from_model(c).to_dict() for c in customers]
    return api_success(data=customers_data)


# =============================================================================
# Address Endpoints
# =============================================================================

@bp.route('/customers/<uuid:customer_id>/addresses', methods=['GET'])
def list_customer_addresses(customer_id):
    """Get all addresses for a customer."""
    service = get_customer_service()
    
    address_type = request.args.get('type')  # billing or shipping
    
    addresses = service.get_addresses(customer_id, address_type)
    addresses_data = [AddressSchema.from_model(a).to_dict() for a in addresses]
    return api_success(data=addresses_data)


@bp.route('/customers/<uuid:customer_id>/addresses', methods=['POST'])
def add_customer_address(customer_id):
    """
    Add address to customer.
    
    Request body:
        street: Street address (required)
        city: City (required)
        state: State/Province (optional)
        zip_code: ZIP/Postal code (required)
        country: Country (optional, default "USA")
        address_type: "billing" or "shipping" (optional, default "billing")
        is_primary: Set as primary address (optional, default false)
    """
    service = get_customer_service()
    data = request.get_json() or {}
    
    try:
        address = service.add_address(
            customer_id=customer_id,
            street=data.get('street', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            zip_code=data.get('zip_code', ''),
            country=data.get('country', 'USA'),
            address_type=data.get('address_type', 'billing'),
            is_primary=data.get('is_primary', False)
        )
        
        address_data = AddressSchema.from_model(address).to_dict()
        return jsonify({
            'success': True,
            'data': address_data,
            'message': 'Address added successfully'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_not_found('Customer', str(customer_id))


@bp.route('/customers/<uuid:customer_id>/addresses/<uuid:address_id>', methods=['PUT'])
def update_customer_address(customer_id, address_id):
    """
    Update an address.
    
    Request body (all optional):
        street, city, state, zip_code, country, is_primary
    """
    service = get_customer_service()
    data = request.get_json() or {}
    
    try:
        address = service.update_address(
            address_id=address_id,
            **data
        )
        
        address_data = AddressSchema.from_model(address).to_dict()
        return api_success(data=address_data, message='Address updated successfully')
        
    except NotFoundError as e:
        return api_not_found('Address', str(address_id))


@bp.route('/customers/<uuid:customer_id>/addresses/<uuid:address_id>', methods=['DELETE'])
def delete_customer_address(customer_id, address_id):
    """Delete an address."""
    service = get_customer_service()
    
    try:
        service.delete_address(address_id)
        return api_success(message='Address deleted successfully')
        
    except NotFoundError as e:
        return api_not_found('Address', str(address_id))


@bp.route('/customers/<uuid:customer_id>/addresses/primary', methods=['GET'])
def get_primary_address(customer_id):
    """Get customer's primary address."""
    service = get_customer_service()
    
    address_type = request.args.get('type', 'billing')
    
    address = service.get_primary_address(customer_id, address_type)
    if not address:
        return api_not_found('Primary Address', f'customer {customer_id}')
    
    address_data = AddressSchema.from_model(address).to_dict()
    return api_success(data=address_data)
