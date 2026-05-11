"""
Customer Service
================

Business logic for customer management.
Handles customer profile creation and management.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from app.models import Customer, Address, User
from app.repositories import CustomerRepository, AddressRepository
from app.services.base import BaseService, ValidationError, NotFoundError
from app.services.user_service import UserService
from app.utils.validators import validate_phone, validate_required
from app.extensions import db


class CustomerService(BaseService[Customer]):
    """
    Service for customer management operations.
    """
    
    def __init__(
        self,
        repository: CustomerRepository = None,
        address_repository: AddressRepository = None,
        user_service: UserService = None
    ):
        self.repository = repository or CustomerRepository()
        self.address_repository = address_repository or AddressRepository()
        self.user_service = user_service or UserService()
    
    # =========================================================================
    # Customer Creation
    # =========================================================================
    
    def create_customer(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        company_name: Optional[str] = None,
        phone: Optional[str] = None,
        credit_terms: str = 'Net 30',
        auto_commit: bool = True
    ) -> Customer:
        """
        Create a new customer with user account.
        
        This is the main registration method - creates both User and Customer.
        
        Args:
            email: Customer email
            password: Account password
            first_name: First name
            last_name: Last name
            company_name: Optional company name
            phone: Optional phone number
            credit_terms: Payment terms
            auto_commit: Whether to commit transaction
            
        Returns:
            Created Customer instance
        """
        # Validate phone if provided
        if phone:
            is_valid, error = validate_phone(phone)
            if not is_valid:
                raise ValidationError([f"Phone: {error}"])
        
        # Create user account
        user = self.user_service.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='customer',
            auto_commit=False
        )
        
        # Create customer profile
        customer = Customer(
            user_id=user.id,
            company_name=company_name.strip() if company_name else None,
            phone=phone.strip() if phone else None,
            credit_terms=credit_terms
        )
        
        db.session.add(customer)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return customer
    
    def create_customer_for_user(
        self,
        user_id: UUID,
        company_name: Optional[str] = None,
        phone: Optional[str] = None,
        credit_terms: str = 'Net 30',
        auto_commit: bool = True
    ) -> Customer:
        """
        Create customer profile for existing user.
        
        Args:
            user_id: Existing user ID
            company_name: Optional company name
            phone: Optional phone number
            credit_terms: Payment terms
            auto_commit: Whether to commit transaction
            
        Returns:
            Created Customer instance
        """
        # Verify user exists
        user = self.user_service.get_or_404(user_id, "User")
        
        # Check if customer profile already exists
        existing = self.repository.get_by_user_id(user_id)
        if existing:
            raise ValidationError(["Customer profile already exists for this user"])
        
        customer = Customer(
            user_id=user_id,
            company_name=company_name.strip() if company_name else None,
            phone=phone.strip() if phone else None,
            credit_terms=credit_terms
        )
        
        db.session.add(customer)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return customer
    
    # =========================================================================
    # Customer Queries
    # =========================================================================
    
    def get_by_user_id(self, user_id: UUID) -> Optional[Customer]:
        """Get customer by their user ID."""
        return self.repository.get_by_user_id(user_id)
    
    def search_customers(
        self,
        query: str,
        active_only: bool = True
    ) -> List[Customer]:
        """
        Search customers by name, company, or email.
        
        Args:
            query: Search string
            active_only: Only return active customers
            
        Returns:
            List of matching Customer instances
        """
        return self.repository.search(query, active_only)
    
    def get_with_pending_requests(self) -> List[Customer]:
        """Get customers with pending book requests."""
        return self.repository.get_with_pending_requests()
    
    def get_with_unpaid_invoices(self) -> List[Customer]:
        """Get customers with unpaid invoices."""
        return self.repository.get_with_unpaid_invoices()
    
    # =========================================================================
    # Profile Updates
    # =========================================================================
    
    def update_customer(
        self,
        customer_id: UUID,
        company_name: Optional[str] = None,
        phone: Optional[str] = None,
        notes: Optional[str] = None,
        credit_terms: Optional[str] = None,
        auto_commit: bool = True
    ) -> Customer:
        """
        Update customer profile.
        
        Args:
            customer_id: Customer ID
            company_name: New company name
            phone: New phone number
            notes: Internal notes
            credit_terms: Payment terms
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated Customer instance
        """
        customer = self.get_or_404(customer_id, "Customer")
        
        if company_name is not None:
            customer.company_name = company_name.strip() if company_name else None
        
        if phone is not None:
            if phone:
                is_valid, error = validate_phone(phone)
                if not is_valid:
                    raise ValidationError([f"Phone: {error}"])
            customer.phone = phone.strip() if phone else None
        
        if notes is not None:
            customer.notes = notes.strip() if notes else None
        
        if credit_terms is not None:
            customer.credit_terms = credit_terms
        
        if auto_commit:
            self.commit()
        
        return customer
    
    # =========================================================================
    # Address Management
    # =========================================================================
    
    def add_address(
        self,
        customer_id: UUID,
        street: str,
        city: str,
        state: str,
        zip_code: str,
        country: str = 'USA',
        address_type: str = 'billing',
        is_primary: bool = False,
        auto_commit: bool = True
    ) -> Address:
        """
        Add address to customer.
        
        Args:
            customer_id: Customer ID
            street: Street address
            city: City
            state: State/Province
            zip_code: ZIP/Postal code
            country: Country
            address_type: 'billing' or 'shipping'
            is_primary: Whether this is the primary address
            auto_commit: Whether to commit transaction
            
        Returns:
            Created Address instance
        """
        # Verify customer exists
        customer = self.get_or_404(customer_id, "Customer")
        
        # Validate inputs
        errors = []
        
        is_valid, error = validate_required(street, "Street")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_required(city, "City")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = validate_required(zip_code, "ZIP code")
        if not is_valid:
            errors.append(error)
        
        if address_type not in ('billing', 'shipping'):
            errors.append("Address type must be 'billing' or 'shipping'")
        
        self.validate_and_raise(errors)
        
        # Create address
        address = Address(
            customer_id=customer_id,
            address_type=address_type,
            street=street.strip(),
            city=city.strip(),
            state=state.strip() if state else None,
            zip_code=zip_code.strip(),
            country=country.strip(),
            is_primary=is_primary
        )
        
        db.session.add(address)
        
        # If primary, unset other primaries of same type
        if is_primary:
            self.flush()
            self.address_repository.set_primary(address)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return address
    
    def update_address(
        self,
        address_id: UUID,
        **kwargs
    ) -> Address:
        """
        Update an address.
        
        Args:
            address_id: Address ID
            **kwargs: Fields to update
            
        Returns:
            Updated Address instance
        """
        address = self.address_repository.get_by_id(address_id)
        if not address:
            raise NotFoundError("Address", address_id)
        
        allowed_fields = ['street', 'city', 'state', 'zip_code', 'country']
        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                setattr(address, field, kwargs[field].strip())
        
        if kwargs.get('is_primary'):
            self.address_repository.set_primary(address)
        
        self.commit()
        return address
    
    def delete_address(self, address_id: UUID, auto_commit: bool = True) -> bool:
        """
        Delete an address.
        
        Args:
            address_id: Address ID
            auto_commit: Whether to commit transaction
            
        Returns:
            True if deleted
        """
        address = self.address_repository.get_by_id(address_id)
        if not address:
            raise NotFoundError("Address", address_id)
        
        self.address_repository.delete(address)
        
        if auto_commit:
            self.commit()
        
        return True
    
    def get_addresses(
        self,
        customer_id: UUID,
        address_type: Optional[str] = None
    ) -> List[Address]:
        """
        Get addresses for a customer.
        
        Args:
            customer_id: Customer ID
            address_type: Optional type filter
            
        Returns:
            List of Address instances
        """
        return self.address_repository.get_by_customer(customer_id, address_type)
    
    def get_primary_address(
        self,
        customer_id: UUID,
        address_type: str = 'billing'
    ) -> Optional[Address]:
        """
        Get customer's primary address.
        
        Args:
            customer_id: Customer ID
            address_type: Address type
            
        Returns:
            Primary Address or None
        """
        return self.address_repository.get_primary(customer_id, address_type)
