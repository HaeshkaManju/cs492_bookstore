"""
Base Service
============

Abstract base service providing common functionality.

Design: Template Method Pattern
- Base class provides common operations
- Subclasses implement domain-specific logic
"""

from typing import TypeVar, Generic, Optional, Dict, Any, List
from uuid import UUID

from app.repositories.base import BaseRepository
from app.extensions import db

T = TypeVar('T')


class ServiceError(Exception):
    """Base exception for service layer errors."""
    
    def __init__(self, message: str, code: str = None, details: Dict = None):
        super().__init__(message)
        self.message = message
        self.code = code or 'SERVICE_ERROR'
        self.details = details or {}


class ValidationError(ServiceError):
    """Raised when input validation fails."""
    
    def __init__(self, errors: List[str]):
        super().__init__(
            message="Validation failed",
            code='VALIDATION_ERROR',
            details={'errors': errors}
        )
        self.errors = errors


class NotFoundError(ServiceError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, id: Any):
        super().__init__(
            message=f"{resource} not found: {id}",
            code='NOT_FOUND',
            details={'resource': resource, 'id': str(id)}
        )
        self.resource_type = resource
        self.resource_id = id


class ConflictError(ServiceError):
    """Raised when an operation conflicts with current state."""
    
    def __init__(self, message: str, details: Dict = None):
        super().__init__(
            message=message,
            code='CONFLICT',
            details=details or {}
        )


class BaseService(Generic[T]):
    """
    Base service with common functionality.
    
    Provides:
    - Transaction management (commit/rollback)
    - Common CRUD wrappers
    - Error handling utilities
    
    Subclasses should:
    - Set repository attribute
    - Implement domain-specific business logic
    """
    
    repository: BaseRepository = None
    
    def __init__(self, repository: BaseRepository = None):
        """
        Initialize service with optional repository injection.
        
        Args:
            repository: Repository instance (for dependency injection/testing)
        """
        if repository:
            self.repository = repository
    
    # =========================================================================
    # Transaction Management
    # =========================================================================
    
    def commit(self) -> None:
        """Commit current database transaction."""
        db.session.commit()
    
    def rollback(self) -> None:
        """Rollback current database transaction."""
        db.session.rollback()
    
    def flush(self) -> None:
        """Flush pending changes without committing."""
        db.session.flush()
    
    # =========================================================================
    # Common Operations
    # =========================================================================
    
    def get_by_id(self, id: UUID) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            id: Entity UUID
            
        Returns:
            Entity instance or None
        """
        return self.repository.get_by_id(id)
    
    def get_or_404(self, id: UUID, resource_name: str = "Resource") -> T:
        """
        Get entity by ID or raise NotFoundError.
        
        Args:
            id: Entity UUID
            resource_name: Name for error message
            
        Returns:
            Entity instance
            
        Raises:
            NotFoundError: If entity not found
        """
        entity = self.get_by_id(id)
        if not entity:
            raise NotFoundError(resource_name, id)
        return entity
    
    def exists(self, **kwargs) -> bool:
        """Check if entity exists matching criteria."""
        return self.repository.exists(**kwargs)
    
    # =========================================================================
    # Validation Helpers
    # =========================================================================
    
    def validate_and_raise(self, errors: List[str]) -> None:
        """
        Raise ValidationError if errors list is not empty.
        
        Args:
            errors: List of error messages
            
        Raises:
            ValidationError: If errors is not empty
        """
        if errors:
            raise ValidationError(errors)
