"""
Base Repository
===============

Abstract base repository implementing common CRUD operations.
All domain repositories inherit from this class.

Design Pattern: Template Method Pattern
- Base class defines common algorithm structure
- Subclasses override specific steps

Generic Type Parameter:
- T: The SQLAlchemy model type this repository manages
"""

from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Query

from app.extensions import db

# Generic type for models
T = TypeVar('T', bound=db.Model)


class BaseRepository(Generic[T]):
    """
    Base repository with common CRUD operations.
    
    Provides:
    - get_by_id: Find single record by primary key
    - get_all: Get all records with pagination
    - create: Create new record
    - update: Update existing record
    - delete: Delete record
    - find_by: Find records matching criteria
    
    Subclasses should:
    - Set model_class attribute
    - Add domain-specific query methods
    """
    
    # Subclasses must set this to the SQLAlchemy model class
    model_class: Type[T] = None
    
    def __init__(self):
        """Initialize repository with model class validation."""
        if self.model_class is None:
            raise ValueError(
                f"{self.__class__.__name__} must define model_class attribute"
            )
    
    # =========================================================================
    # Read Operations
    # =========================================================================
    
    def get_by_id(self, id: UUID) -> Optional[T]:
        """
        Get single record by ID.
        
        Args:
            id: Primary key UUID
            
        Returns:
            Model instance or None if not found
        """
        return self.model_class.query.get(id)
    
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        order_by: str = None,
        descending: bool = False
    ) -> Dict[str, Any]:
        """
        Get all records with pagination.
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            order_by: Column name to order by
            descending: Sort descending if True
            
        Returns:
            Dict with 'items', 'total', 'page', 'pages', 'per_page'
        """
        query = self._base_query()
        
        # Apply ordering
        if order_by:
            column = getattr(self.model_class, order_by, None)
            if column is not None:
                if descending:
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    def find_by(self, **kwargs) -> List[T]:
        """
        Find records matching exact field values.
        
        Args:
            **kwargs: Field=value pairs to match
            
        Returns:
            List of matching model instances
        """
        return self.model_class.query.filter_by(**kwargs).all()
    
    def find_one_by(self, **kwargs) -> Optional[T]:
        """
        Find single record matching exact field values.
        
        Args:
            **kwargs: Field=value pairs to match
            
        Returns:
            Model instance or None
        """
        return self.model_class.query.filter_by(**kwargs).first()
    
    def exists(self, **kwargs) -> bool:
        """
        Check if record exists matching criteria.
        
        Args:
            **kwargs: Field=value pairs to match
            
        Returns:
            True if matching record exists
        """
        return self.model_class.query.filter_by(**kwargs).count() > 0
    
    def count(self, **kwargs) -> int:
        """
        Count records matching criteria.
        
        Args:
            **kwargs: Field=value pairs to match (empty = count all)
            
        Returns:
            Number of matching records
        """
        if kwargs:
            return self.model_class.query.filter_by(**kwargs).count()
        return self.model_class.query.count()
    
    # =========================================================================
    # Write Operations
    # =========================================================================
    
    def create(self, **kwargs) -> T:
        """
        Create new record.
        
        Args:
            **kwargs: Field values for new record
            
        Returns:
            Created model instance (with ID)
        """
        instance = self.model_class(**kwargs)
        db.session.add(instance)
        db.session.flush()  # Get ID without committing
        return instance
    
    def update(self, instance: T, **kwargs) -> T:
        """
        Update existing record.
        
        Args:
            instance: Model instance to update
            **kwargs: Field values to update
            
        Returns:
            Updated model instance
        """
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.flush()
        return instance
    
    def delete(self, instance: T) -> bool:
        """
        Delete record.
        
        Args:
            instance: Model instance to delete
            
        Returns:
            True if deleted successfully
        """
        db.session.delete(instance)
        db.session.flush()
        return True
    
    def soft_delete(self, instance: T) -> T:
        """
        Soft delete record (set is_active=False).
        
        Args:
            instance: Model instance to soft delete
            
        Returns:
            Updated model instance
        """
        if hasattr(instance, 'is_active'):
            instance.is_active = False
            db.session.flush()
        return instance
    
    # =========================================================================
    # Transaction Management
    # =========================================================================
    
    def commit(self) -> None:
        """Commit current transaction."""
        db.session.commit()
    
    def rollback(self) -> None:
        """Rollback current transaction."""
        db.session.rollback()
    
    def flush(self) -> None:
        """Flush pending changes without committing."""
        db.session.flush()
    
    # =========================================================================
    # Query Building
    # =========================================================================
    
    def _base_query(self) -> Query:
        """
        Get base query for this repository.
        
        Override in subclasses to add default filters (e.g., active only).
        
        Returns:
            SQLAlchemy Query object
        """
        return self.model_class.query
    
    def _active_query(self) -> Query:
        """
        Get query filtered to active records only.
        
        Returns:
            SQLAlchemy Query object
        """
        if hasattr(self.model_class, 'is_active'):
            return self.model_class.query.filter_by(is_active=True)
        return self._base_query()
