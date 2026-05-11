"""
Customer Repository
===================

Data access for Customer and Address models.
"""

from typing import Optional, List
from uuid import UUID

from app.models import Customer, Address
from app.repositories.base import BaseRepository
from app.extensions import db


class CustomerRepository(BaseRepository[Customer]):
    """
    Repository for Customer data access.
    """
    
    model_class = Customer
    
    def get_by_user_id(self, user_id: UUID) -> Optional[Customer]:
        """
        Get customer profile by user ID.
        
        Args:
            user_id: Associated user's ID
            
        Returns:
            Customer instance or None
        """
        return Customer.query.filter_by(user_id=user_id).first()
    
    def get_with_user(self, customer_id: UUID) -> Optional[Customer]:
        """
        Get customer with user data eagerly loaded.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Customer instance with user data
        """
        return Customer.query.options(
            db.joinedload(Customer.user)
        ).get(customer_id)
    
    def search(
        self,
        query_str: str,
        active_only: bool = True
    ) -> List[Customer]:
        """
        Search customers by name, company, or email.
        
        Args:
            query_str: Search string
            active_only: Only return active customers
            
        Returns:
            List of matching Customer instances
        """
        from app.models import User
        
        search = f"%{query_str}%"
        
        query = Customer.query.join(User).filter(
            (User.email.ilike(search)) |
            (User.first_name.ilike(search)) |
            (User.last_name.ilike(search)) |
            (Customer.company_name.ilike(search))
        )
        
        if active_only:
            query = query.filter(Customer.is_active == True)
        
        return query.order_by(User.last_name, User.first_name).all()
    
    def get_with_pending_requests(self) -> List[Customer]:
        """
        Get customers with pending book requests.
        
        Returns:
            List of customers with pending requests
        """
        from app.models import BookRequest
        
        return Customer.query.join(BookRequest).filter(
            BookRequest.status == 'pending',
            Customer.is_active == True
        ).distinct().all()
    
    def get_with_unpaid_invoices(self) -> List[Customer]:
        """
        Get customers with unpaid invoices.
        
        Returns:
            List of customers with sent (unpaid) invoices
        """
        from app.models import Invoice
        
        return Customer.query.join(Invoice).filter(
            Invoice.status == 'sent',
            Customer.is_active == True
        ).distinct().all()


class AddressRepository(BaseRepository[Address]):
    """
    Repository for Address data access.
    """
    
    model_class = Address
    
    def get_by_customer(
        self,
        customer_id: UUID,
        address_type: Optional[str] = None
    ) -> List[Address]:
        """
        Get addresses for a customer.
        
        Args:
            customer_id: Customer ID
            address_type: Optional filter by type (billing/shipping)
            
        Returns:
            List of Address instances
        """
        query = Address.query.filter_by(customer_id=customer_id)
        
        if address_type:
            query = query.filter_by(address_type=address_type)
        
        return query.order_by(Address.is_primary.desc()).all()
    
    def get_primary(
        self,
        customer_id: UUID,
        address_type: str = 'billing'
    ) -> Optional[Address]:
        """
        Get primary address for customer.
        
        Args:
            customer_id: Customer ID
            address_type: Address type (billing/shipping)
            
        Returns:
            Primary Address or None
        """
        return Address.query.filter_by(
            customer_id=customer_id,
            address_type=address_type,
            is_primary=True
        ).first()
    
    def set_primary(
        self,
        address: Address
    ) -> Address:
        """
        Set address as primary (and unset others of same type).
        
        Args:
            address: Address to make primary
            
        Returns:
            Updated Address instance
        """
        # Unset other primaries of same type
        Address.query.filter(
            Address.customer_id == address.customer_id,
            Address.address_type == address.address_type,
            Address.id != address.id
        ).update({'is_primary': False})
        
        address.is_primary = True
        db.session.flush()
        return address
