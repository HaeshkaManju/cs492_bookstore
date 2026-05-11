"""
Base Schema
===========

Base class for all DTOs providing common serialization functionality.
"""

from typing import Dict, Any, Optional, TypeVar, Type
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass, field, asdict


T = TypeVar('T')


@dataclass
class BaseSchema:
    """
    Base schema providing common serialization methods.
    
    All DTOs inherit from this class.
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert schema to dictionary.
        
        Handles UUID and datetime serialization.
        """
        result = {}
        for key, value in asdict(self).items():
            if value is None:
                result[key] = None
            elif isinstance(value, UUID):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in value
                ]
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create schema from dictionary.
        
        Subclasses may override for custom parsing.
        """
        # Filter to only known fields
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)
    
    @classmethod
    def from_model(cls: Type[T], model: Any) -> T:
        """
        Create schema from SQLAlchemy model.
        
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement from_model")


def parse_uuid(value: Any) -> Optional[UUID]:
    """Parse value to UUID."""
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


def parse_datetime(value: Any) -> Optional[datetime]:
    """Parse value to datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))
