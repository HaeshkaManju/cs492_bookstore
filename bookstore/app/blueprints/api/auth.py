"""
Authentication API Endpoints
============================

REST API for authentication and authorization.
Task: AUTH-S2-001
"""

from flask import request, jsonify, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta
from uuid import UUID

from app.blueprints.api import bp
from app.api import get_user_service, api_success, api_error, api_validation_error
from app.services.base import ValidationError, NotFoundError, ConflictError
from app.schemas import UserSchema


def _generate_tokens(user):
    """Generate access and refresh tokens for a user."""
    secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
    
    # Access token - short lived (15 minutes)
    access_payload = {
        'user_id': str(user.id),
        'email': user.email,
        'role': user.role,
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=15),
        'iat': datetime.utcnow()
    }
    access_token = jwt.encode(access_payload, secret_key, algorithm='HS256')
    
    # Refresh token - long lived (7 days)
    refresh_payload = {
        'user_id': str(user.id),
        'type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    refresh_token = jwt.encode(refresh_payload, secret_key, algorithm='HS256')
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': 900  # 15 minutes in seconds
    }


def _decode_token(token, token_type='access'):
    """Decode and validate a JWT token."""
    secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        if payload.get('type') != token_type:
            return None, 'Invalid token type'
        
        return payload, None
        
    except jwt.ExpiredSignatureError:
        return None, 'Token has expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'


def jwt_required(f):
    """Decorator to require JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return api_error('Authorization header required', code='UNAUTHORIZED', status=401)
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return api_error('Invalid authorization header format', code='UNAUTHORIZED', status=401)
        
        token = parts[1]
        payload, error = _decode_token(token, 'access')
        
        if error:
            return api_error(error, code='UNAUTHORIZED', status=401)
        
        # Add user info to request context
        request.current_user_id = UUID(payload['user_id'])
        request.current_user_role = payload['role']
        request.current_user_email = payload['email']
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        if request.current_user_role != 'admin':
            return api_error('Admin access required', code='FORBIDDEN', status=403)
        return f(*args, **kwargs)
    
    return decorated


def staff_required(f):
    """Decorator to require admin or employee role."""
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        if request.current_user_role not in ('admin', 'employee'):
            return api_error('Staff access required', code='FORBIDDEN', status=403)
        return f(*args, **kwargs)
    
    return decorated


# =============================================================================
# Authentication Endpoints
# =============================================================================

@bp.route('/auth/login', methods=['POST'])
def login():
    """
    Authenticate user and return tokens.
    
    Request body:
        email: User email (required)
        password: User password (required)
    
    Returns:
        access_token: JWT access token (15 min expiry)
        refresh_token: JWT refresh token (7 day expiry)
        token_type: "Bearer"
        expires_in: Seconds until access token expires
        user: User profile data
    """
    service = get_user_service()
    data = request.get_json() or {}
    
    email = data.get('email', '')
    password = data.get('password', '')
    
    if not email or not password:
        return api_validation_error(['Email and password are required'])
    
    user = service.authenticate(email, password)
    
    if not user:
        return api_error('Invalid email or password', code='UNAUTHORIZED', status=401)
    
    tokens = _generate_tokens(user)
    user_data = UserSchema.from_model(user).to_dict()
    
    return jsonify({
        'success': True,
        'data': {
            **tokens,
            'user': user_data
        },
        'message': 'Login successful'
    }), 200


@bp.route('/auth/register', methods=['POST'])
def register():
    """
    Register a new customer account.
    
    Request body:
        email: User email (required)
        password: Password (required)
        first_name: First name (required)
        last_name: Last name (required)
    
    Returns tokens and user profile.
    """
    service = get_user_service()
    data = request.get_json() or {}
    
    try:
        user = service.create_user(
            email=data.get('email', ''),
            password=data.get('password', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role='customer'
        )
        
        tokens = _generate_tokens(user)
        user_data = UserSchema.from_model(user).to_dict()
        
        return jsonify({
            'success': True,
            'data': {
                **tokens,
                'user': user_data
            },
            'message': 'Registration successful'
        }), 201
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except ConflictError as e:
        return api_error(e.message, code='CONFLICT', status=409)


@bp.route('/auth/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh access token using refresh token.
    
    Request body:
        refresh_token: Valid refresh token (required)
    
    Returns new access token.
    """
    data = request.get_json() or {}
    refresh_token = data.get('refresh_token', '')
    
    if not refresh_token:
        return api_validation_error(['Refresh token is required'])
    
    payload, error = _decode_token(refresh_token, 'refresh')
    
    if error:
        return api_error(error, code='UNAUTHORIZED', status=401)
    
    # Get user to verify still active
    service = get_user_service()
    user = service.get_by_id(UUID(payload['user_id']))
    
    if not user or not user.is_active:
        return api_error('User not found or inactive', code='UNAUTHORIZED', status=401)
    
    tokens = _generate_tokens(user)
    
    return jsonify({
        'success': True,
        'data': tokens,
        'message': 'Token refreshed successfully'
    }), 200


@bp.route('/auth/me', methods=['GET'])
@jwt_required
def get_current_user():
    """Get current authenticated user profile."""
    service = get_user_service()
    
    user = service.get_by_id(request.current_user_id)
    if not user:
        return api_error('User not found', code='NOT_FOUND', status=404)
    
    user_data = UserSchema.from_model(user).to_dict()
    return api_success(data=user_data)


@bp.route('/auth/me', methods=['PUT'])
@jwt_required
def update_current_user():
    """
    Update current user profile.
    
    Request body (all optional):
        first_name, last_name
    """
    service = get_user_service()
    data = request.get_json() or {}
    
    try:
        user = service.update_profile(
            user_id=request.current_user_id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        user_data = UserSchema.from_model(user).to_dict()
        return api_success(data=user_data, message='Profile updated successfully')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_error('User not found', code='NOT_FOUND', status=404)


@bp.route('/auth/password', methods=['PUT'])
@jwt_required
def change_password():
    """
    Change current user's password.
    
    Request body:
        current_password: Current password (required)
        new_password: New password (required)
    """
    service = get_user_service()
    data = request.get_json() or {}
    
    try:
        service.change_password(
            user_id=request.current_user_id,
            current_password=data.get('current_password', ''),
            new_password=data.get('new_password', '')
        )
        
        return api_success(message='Password changed successfully')
        
    except ValidationError as e:
        return api_validation_error(e.errors)
    except NotFoundError as e:
        return api_error('User not found', code='NOT_FOUND', status=404)


@bp.route('/auth/logout', methods=['POST'])
@jwt_required
def logout():
    """
    Logout user (invalidate tokens).
    
    Note: With stateless JWT, we can't truly invalidate tokens.
    Client should discard tokens. For true invalidation,
    implement a token blacklist.
    """
    # In a production system, you would add the token to a blacklist
    # For now, we just return success
    return api_success(message='Logged out successfully')


@bp.route('/auth/validate', methods=['GET'])
@jwt_required
def validate_token():
    """Validate current access token."""
    return api_success(data={
        'valid': True,
        'user_id': str(request.current_user_id),
        'role': request.current_user_role
    })
