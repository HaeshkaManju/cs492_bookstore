"""
User Repository
===============

Data access for User model.
Handles user lookups, creation, and authentication-related queries.
"""

from typing import Optional, List

from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User data access.
    
    Provides user-specific queries beyond basic CRUD.
    """
    
    model_class = User
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Find user by email address.
        
        Args:
            email: Email to search for (case-insensitive)
            
        Returns:
            User instance or None
        """
        return User.query.filter(
            User.email.ilike(email.lower().strip())
        ).first()
    
    def email_exists(self, email: str, exclude_id: str = None) -> bool:
        """
        Check if email is already registered.
        
        Args:
            email: Email to check
            exclude_id: User ID to exclude (for updates)
            
        Returns:
            True if email exists
        """
        query = User.query.filter(User.email.ilike(email.lower().strip()))
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        return query.count() > 0
    
    def get_by_role(self, role: str, active_only: bool = True) -> List[User]:
        """
        Get all users with a specific role.
        
        Args:
            role: Role to filter by (admin, employee, customer)
            active_only: Only return active users
            
        Returns:
            List of User instances
        """
        query = User.query.filter_by(role=role)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(User.last_name, User.first_name).all()
    
    def get_staff(self, active_only: bool = True) -> List[User]:
        """
        Get all staff users (admin and employee).
        
        Args:
            active_only: Only return active users
            
        Returns:
            List of User instances
        """
        query = User.query.filter(User.role.in_(['admin', 'employee']))
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(User.role, User.last_name).all()
    
    def get_customers(self, active_only: bool = True) -> List[User]:
        """
        Get all customer users.
        
        Args:
            active_only: Only return active users
            
        Returns:
            List of User instances
        """
        return self.get_by_role('customer', active_only)
    
    def search(
        self,
        query_str: str,
        role: Optional[str] = None,
        active_only: bool = True
    ) -> List[User]:
        """
        Search users by name or email.
        
        Args:
            query_str: Search string
            role: Optional role filter
            active_only: Only return active users
            
        Returns:
            List of matching User instances
        """
        search = f"%{query_str}%"
        
        query = User.query.filter(
            (User.email.ilike(search)) |
            (User.first_name.ilike(search)) |
            (User.last_name.ilike(search))
        )
        
        if role:
            query = query.filter_by(role=role)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.order_by(User.last_name, User.first_name).all()
    
    def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str = 'customer'
    ) -> User:
        """
        Create new user with hashed password.
        
        Args:
            email: User email
            password: Plain text password (will be hashed)
            first_name: User's first name
            last_name: User's last name
            role: User role (default: customer)
            
        Returns:
            Created User instance
        """
        user = User(
            email=email.lower().strip(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role=role
        )
        user.set_password(password)
        
        self._session.add(user)
        self._session.flush()
        return user
    
    @property
    def _session(self):
        from app.extensions import db
        return db.session
