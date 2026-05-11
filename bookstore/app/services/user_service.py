"""
User Service
============

Business logic for user management.
Handles user creation, authentication validation, and profile updates.

Note: RBAC (role enforcement) will be handled separately.
This service focuses on user data operations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from app.models import User
from app.repositories import UserRepository
from app.services.base import BaseService, ValidationError, NotFoundError, ConflictError
from app.utils.validators import (
    validate_email,
    validate_password,
    validate_password_match,
    validate_name,
    validate_registration_data
)


class UserService(BaseService[User]):
    """
    Service for user management operations.
    """
    
    def __init__(self, repository: UserRepository = None):
        self.repository = repository or UserRepository()
    
    # =========================================================================
    # User Creation
    # =========================================================================
    
    def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str = 'customer',
        auto_commit: bool = True
    ) -> User:
        """
        Create a new user account.
        
        Args:
            email: User email (must be unique)
            password: Plain text password (will be validated and hashed)
            first_name: User's first name
            last_name: User's last name
            role: User role (admin/employee/customer)
            auto_commit: Whether to commit transaction
            
        Returns:
            Created User instance
            
        Raises:
            ValidationError: If input validation fails
            ConflictError: If email already exists
        """
        # Validate inputs
        errors = validate_registration_data({
            'email': email,
            'password': password,
            'confirm_password': password,  # Service doesn't need confirmation
            'first_name': first_name,
            'last_name': last_name
        })
        self.validate_and_raise(errors)
        
        # Check email uniqueness
        if self.repository.email_exists(email):
            raise ConflictError(
                "Email address is already registered",
                {'email': email}
            )
        
        # Validate role
        if role not in ('admin', 'employee', 'customer'):
            raise ValidationError([f"Invalid role: {role}"])
        
        # Create user
        user = User(
            email=email.lower().strip(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role=role
        )
        user.set_password(password)
        
        from app.extensions import db
        db.session.add(user)
        
        if auto_commit:
            self.commit()
        else:
            self.flush()
        
        return user
    
    # =========================================================================
    # User Queries
    # =========================================================================
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Find user by email address.
        
        Args:
            email: Email to search for
            
        Returns:
            User instance or None
        """
        return self.repository.get_by_email(email)
    
    def get_by_role(self, role: str, active_only: bool = True) -> List[User]:
        """
        Get all users with a specific role.
        
        Args:
            role: Role to filter by
            active_only: Only return active users
            
        Returns:
            List of User instances
        """
        return self.repository.get_by_role(role, active_only)
    
    def get_staff(self, active_only: bool = True) -> List[User]:
        """Get all staff users (admin and employee)."""
        return self.repository.get_staff(active_only)
    
    def search_users(
        self,
        query: str,
        role: Optional[str] = None,
        active_only: bool = True
    ) -> List[User]:
        """
        Search users by name or email.
        
        Args:
            query: Search string
            role: Optional role filter
            active_only: Only return active users
            
        Returns:
            List of matching User instances
        """
        return self.repository.search(query, role, active_only)
    
    # =========================================================================
    # Authentication Support
    # =========================================================================
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Validate user credentials.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            User instance if credentials valid, None otherwise
        """
        user = self.get_by_email(email)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not user.check_password(password):
            return None
        
        return user
    
    # =========================================================================
    # Profile Updates
    # =========================================================================
    
    def update_profile(
        self,
        user_id: UUID,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        auto_commit: bool = True
    ) -> User:
        """
        Update user profile information.
        
        Args:
            user_id: User ID to update
            first_name: New first name (optional)
            last_name: New last name (optional)
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated User instance
        """
        user = self.get_or_404(user_id, "User")
        
        errors = []
        
        if first_name is not None:
            is_valid, error = validate_name(first_name, "First name")
            if not is_valid:
                errors.append(error)
            else:
                user.first_name = first_name.strip()
        
        if last_name is not None:
            is_valid, error = validate_name(last_name, "Last name")
            if not is_valid:
                errors.append(error)
            else:
                user.last_name = last_name.strip()
        
        self.validate_and_raise(errors)
        
        if auto_commit:
            self.commit()
        
        return user
    
    def update_email(
        self,
        user_id: UUID,
        new_email: str,
        auto_commit: bool = True
    ) -> User:
        """
        Update user email address.
        
        Args:
            user_id: User ID to update
            new_email: New email address
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated User instance
            
        Raises:
            ConflictError: If email already in use
        """
        user = self.get_or_404(user_id, "User")
        
        # Validate email
        is_valid, error = validate_email(new_email)
        if not is_valid:
            raise ValidationError([f"Email: {error}"])
        
        # Check uniqueness (excluding current user)
        if self.repository.email_exists(new_email, exclude_id=str(user_id)):
            raise ConflictError(
                "Email address is already in use",
                {'email': new_email}
            )
        
        user.email = new_email.lower().strip()
        
        if auto_commit:
            self.commit()
        
        return user
    
    def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
        auto_commit: bool = True
    ) -> User:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password for verification
            new_password: New password
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated User instance
            
        Raises:
            ValidationError: If current password wrong or new password invalid
        """
        user = self.get_or_404(user_id, "User")
        
        # Verify current password
        if not user.check_password(current_password):
            raise ValidationError(["Current password is incorrect"])
        
        # Validate new password
        is_valid, error = validate_password(new_password)
        if not is_valid:
            raise ValidationError([f"New password: {error}"])
        
        user.set_password(new_password)
        
        if auto_commit:
            self.commit()
        
        return user
    
    # =========================================================================
    # Account Management
    # =========================================================================
    
    def deactivate_user(self, user_id: UUID, auto_commit: bool = True) -> User:
        """
        Deactivate a user account (soft delete).
        
        Args:
            user_id: User ID to deactivate
            auto_commit: Whether to commit transaction
            
        Returns:
            Deactivated User instance
        """
        user = self.get_or_404(user_id, "User")
        user.is_active = False
        
        if auto_commit:
            self.commit()
        
        return user
    
    def reactivate_user(self, user_id: UUID, auto_commit: bool = True) -> User:
        """
        Reactivate a deactivated user account.
        
        Args:
            user_id: User ID to reactivate
            auto_commit: Whether to commit transaction
            
        Returns:
            Reactivated User instance
        """
        user = self.get_or_404(user_id, "User")
        user.is_active = True
        
        if auto_commit:
            self.commit()
        
        return user
    
    def change_role(
        self,
        user_id: UUID,
        new_role: str,
        auto_commit: bool = True
    ) -> User:
        """
        Change user role.
        
        Args:
            user_id: User ID
            new_role: New role (admin/employee/customer)
            auto_commit: Whether to commit transaction
            
        Returns:
            Updated User instance
        """
        if new_role not in ('admin', 'employee', 'customer'):
            raise ValidationError([f"Invalid role: {new_role}"])
        
        user = self.get_or_404(user_id, "User")
        user.role = new_role
        
        if auto_commit:
            self.commit()
        
        return user
