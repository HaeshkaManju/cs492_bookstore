"""
Input Validation Utilities
==========================

Centralized validation logic for all user inputs.

Two interfaces are provided:
1. Boolean functions (validate_email, validate_password, etc.) - return True/False
2. Tuple functions (validate_email_full, etc.) - return (is_valid, error_message)

Design: Pure functions with no side effects
- Easy to test
- Reusable across modules
- Can be called from forms, API endpoints, or services

Usage:
    # Simple boolean check
    from app.utils.validators import validate_email
    if not validate_email('test@example.com'):
        raise ValueError("Invalid email")
    
    # Full validation with error message
    from app.utils.validators import validate_email_full
    is_valid, error = validate_email_full('test@example.com')
    if not is_valid:
        raise ValueError(error)
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Tuple, Optional, List, Union


# Type alias for validation result
ValidationResult = Tuple[bool, Optional[str]]


# =============================================================================
# Exception Classes
# =============================================================================

class ValidationError(Exception):
    """Exception raised when validation fails."""
    
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(', '.join(errors))
    
    def __str__(self):
        return ', '.join(self.errors)


# =============================================================================
# Email Validation
# =============================================================================

def validate_email(email: str) -> bool:
    """
    Validate email format (simple boolean version).
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    is_valid, _ = validate_email_full(email)
    return is_valid


def validate_email_full(email: str) -> ValidationResult:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    try:
        # Try to import email_validator, fall back to regex if not available
        try:
            from email_validator import validate_email as ev, EmailNotValidError
            ev(email, check_deliverability=False)
            return True, None
        except ImportError:
            # Fallback to regex validation
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, email):
                return True, None
            return False, "Invalid email format"
    except Exception as e:
        return False, str(e)


# =============================================================================
# Password Validation
# =============================================================================

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

def validate_password(password: str) -> List[str]:
    """
    Validate password meets security requirements.
    
    Returns list of error messages (empty if valid).
    
    Requirements:
    - 8-128 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if not password:
        errors.append("Password is required")
        return errors
    
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
    
    if len(password) > PASSWORD_MAX_LENGTH:
        errors.append(f"Password must be at most {PASSWORD_MAX_LENGTH} characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', password):
        errors.append("Password must contain at least one special character")
    
    return errors


def validate_password_full(password: str) -> ValidationResult:
    """Validate password and return tuple (for backwards compatibility)."""
    errors = validate_password(password)
    if errors:
        return False, errors[0]
    return True, None


def validate_password_match(password: str, confirm: str) -> ValidationResult:
    """Validate password confirmation matches."""
    if password != confirm:
        return False, "Passwords do not match"
    return True, None


# =============================================================================
# ISBN Validation
# =============================================================================

def validate_isbn(isbn: str) -> bool:
    """
    Validate ISBN-10 or ISBN-13 format and checksum (boolean version).
    
    Args:
        isbn: ISBN string (may include hyphens)
        
    Returns:
        True if valid or empty, False otherwise
    """
    is_valid, _ = validate_isbn_full(isbn)
    return is_valid


def validate_isbn10(isbn: str) -> bool:
    """Validate ISBN-10 format (boolean version)."""
    if not isbn:
        return True
    cleaned = isbn.replace('-', '').replace(' ', '').upper()
    if len(cleaned) != 10:
        return False
    is_valid, _ = _validate_isbn10(cleaned)
    return is_valid


def validate_isbn13(isbn: str) -> bool:
    """Validate ISBN-13 format (boolean version)."""
    if not isbn:
        return True
    cleaned = isbn.replace('-', '').replace(' ', '').upper()
    if len(cleaned) != 13:
        return False
    is_valid, _ = _validate_isbn13(cleaned)
    return is_valid


def validate_isbn_full(isbn: str) -> ValidationResult:
    """
    Validate ISBN-10 or ISBN-13 format and checksum.
    
    Args:
        isbn: ISBN string (may include hyphens)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isbn:
        return True, None  # ISBN is optional for rare books
    
    # Remove hyphens and spaces
    cleaned = isbn.replace('-', '').replace(' ', '').upper()
    
    if len(cleaned) == 10:
        return _validate_isbn10(cleaned)
    elif len(cleaned) == 13:
        return _validate_isbn13(cleaned)
    else:
        return False, "ISBN must be 10 or 13 digits"


def _validate_isbn10(isbn: str) -> ValidationResult:
    """Validate ISBN-10 checksum."""
    if not re.match(r'^[0-9]{9}[0-9X]$', isbn):
        return False, "Invalid ISBN-10 format"
    
    total = 0
    for i, char in enumerate(isbn):
        if char == 'X':
            total += 10 * (10 - i)
        else:
            total += int(char) * (10 - i)
    
    if total % 11 != 0:
        return False, "Invalid ISBN-10 checksum"
    
    return True, None


def _validate_isbn13(isbn: str) -> ValidationResult:
    """Validate ISBN-13 checksum."""
    if not re.match(r'^[0-9]{13}$', isbn):
        return False, "Invalid ISBN-13 format"
    
    total = 0
    for i, char in enumerate(isbn):
        multiplier = 1 if i % 2 == 0 else 3
        total += int(char) * multiplier
    
    if total % 10 != 0:
        return False, "Invalid ISBN-13 checksum"
    
    return True, None


def normalize_isbn(isbn: str) -> str:
    """Remove formatting from ISBN."""
    if not isbn:
        return None
    return isbn.replace('-', '').replace(' ', '').upper()


# =============================================================================
# Money Validation
# =============================================================================

def validate_money(value) -> bool:
    """
    Validate monetary value is a non-negative Decimal (boolean version).
    
    Args:
        value: Should be a Decimal instance
        
    Returns:
        True if valid Decimal >= 0, False otherwise
    """
    if value is None:
        return False
    if not isinstance(value, Decimal):
        return False
    if value < 0:
        return False
    return True


def validate_money_full(
    value,
    allow_zero: bool = False,
    allow_negative: bool = False,
    max_value: Optional[Decimal] = None
) -> ValidationResult:
    """
    Validate monetary value with full options.
    
    Args:
        value: String representation of money or Decimal
        allow_zero: Whether zero is valid
        allow_negative: Whether negative values are valid
        max_value: Maximum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, "Amount is required"
    
    try:
        if isinstance(value, Decimal):
            decimal_value = value
        else:
            decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return False, "Invalid monetary value"
    
    if not allow_negative and decimal_value < 0:
        return False, "Amount cannot be negative"
    
    if not allow_zero and decimal_value == 0:
        return False, "Amount must be greater than zero"
    
    # Check for more than 2 decimal places
    if decimal_value.as_tuple().exponent < -2:
        return False, "Amount can have at most 2 decimal places"
    
    if max_value is not None and decimal_value > max_value:
        return False, f"Amount cannot exceed {max_value}"
    
    return True, None


def parse_money(value: str) -> Optional[Decimal]:
    """Parse string to Decimal for money, returning None on failure."""
    try:
        return Decimal(str(value)).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError):
        return None


# =============================================================================
# Condition Validation
# =============================================================================

CONDITION_MIN = 1
CONDITION_MAX = 5

CONDITION_LABELS = {
    5: 'Fine',
    4: 'Very Good',
    3: 'Good',
    2: 'Fair',
    1: 'Poor'
}

def validate_condition(value) -> bool:
    """
    Validate book condition value (boolean version).
    
    Args:
        value: Condition integer (1-5)
        
    Returns:
        True if valid, False otherwise
    """
    try:
        condition = int(value)
        return CONDITION_MIN <= condition <= CONDITION_MAX
    except (ValueError, TypeError):
        return False


def validate_condition_full(value) -> ValidationResult:
    """
    Validate book condition value (full version).
    
    Args:
        value: Condition integer (1-5)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        condition = int(value)
    except (ValueError, TypeError):
        return False, "Condition must be a number"
    
    if condition < CONDITION_MIN or condition > CONDITION_MAX:
        return False, f"Condition must be between {CONDITION_MIN} (Poor) and {CONDITION_MAX} (Fine)"
    
    return True, None


def get_condition_label(value: int) -> str:
    """Get human-readable condition label."""
    return CONDITION_LABELS.get(value, 'Unknown')


# =============================================================================
# Text Validation
# =============================================================================

def validate_required(value) -> bool:
    """Validate required field is not empty (boolean version)."""
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    return True


def validate_required_full(value: str, field_name: str) -> ValidationResult:
    """Validate required field is not empty (full version)."""
    if not value or not str(value).strip():
        return False, f"{field_name} is required"
    return True, None


def validate_length(value: str, min_len: int = None, max_len: int = None) -> bool:
    """Validate string length (boolean version)."""
    if value is None:
        return min_len is None or min_len == 0
    if min_len is not None and len(value) < min_len:
        return False
    if max_len is not None and len(value) > max_len:
        return False
    return True


def validate_range(value, min_val=None, max_val=None) -> bool:
    """Validate numeric value is within range (boolean version)."""
    if value is None:
        return False
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            return False
        if max_val is not None and num > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False


def validate_max_length(value: str, max_len: int, field_name: str) -> ValidationResult:
    """Validate string length."""
    if value and len(value) > max_len:
        return False, f"{field_name} must be at most {max_len} characters"
    return True, None


def validate_min_length(value: str, min_len: int, field_name: str) -> ValidationResult:
    """Validate minimum string length."""
    if not value or len(value) < min_len:
        return False, f"{field_name} must be at least {min_len} characters"
    return True, None


def validate_name(value: str, field_name: str = "Name") -> ValidationResult:
    """Validate name field (letters, spaces, hyphens, apostrophes)."""
    if not value or not value.strip():
        return False, f"{field_name} is required"
    
    if len(value) > 100:
        return False, f"{field_name} must be at most 100 characters"
    
    if not re.match(r"^[a-zA-Z\s\-'\.]+$", value):
        return False, f"{field_name} contains invalid characters"
    
    return True, None


# =============================================================================
# Phone Validation
# =============================================================================

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (boolean version).
    
    Accepts common formats:
    - (123) 456-7890
    - 123-456-7890
    - 1234567890
    - +1-123-456-7890
    """
    if not phone:
        return True  # Phone is optional
    
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    if not re.match(r'^\+?1?\d{7,14}$', cleaned):
        return False
    
    return True


def validate_phone_full(phone: str) -> ValidationResult:
    """Validate phone number format (full version)."""
    if not phone:
        return True, None  # Phone is optional
    
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    if not re.match(r'^\+?1?\d{7,14}$', cleaned):
        return False, "Invalid phone number format"
    
    return True, None


def normalize_phone(phone: str) -> Optional[str]:
    """Normalize phone to digits only with optional +."""
    if not phone:
        return None
    return re.sub(r'[^\d+]', '', phone)


# =============================================================================
# Quantity Validation
# =============================================================================

def validate_quantity(value) -> bool:
    """Validate quantity is non-negative integer (boolean version)."""
    if value is None:
        return False
    try:
        qty = int(value)
        if qty != float(value):  # Check if it's really an integer
            return False
        return qty >= 0
    except (ValueError, TypeError):
        return False


def validate_quantity_full(
    value,
    field_name: str = "Quantity",
    min_value: int = 1,
    max_value: Optional[int] = None
) -> ValidationResult:
    """Validate quantity is positive integer within range (full version)."""
    try:
        qty = int(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a whole number"
    
    if qty < min_value:
        return False, f"{field_name} must be at least {min_value}"
    
    if max_value is not None and qty > max_value:
        return False, f"{field_name} cannot exceed {max_value}"
    
    return True, None


# =============================================================================
# UUID Validation
# =============================================================================

def validate_uuid(value: str, field_name: str = "ID") -> ValidationResult:
    """Validate UUID format."""
    import uuid
    
    if not value:
        return False, f"{field_name} is required"
    
    try:
        uuid.UUID(str(value))
        return True, None
    except ValueError:
        return False, f"Invalid {field_name} format"


# =============================================================================
# Composite Validators
# =============================================================================

def validate_registration_data(data: dict) -> List[str]:
    """
    Validate all registration form fields.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # Email
    is_valid, error = validate_email(data.get('email', ''))
    if not is_valid:
        errors.append(f"Email: {error}")
    
    # Password
    is_valid, error = validate_password(data.get('password', ''))
    if not is_valid:
        errors.append(f"Password: {error}")
    
    # Password confirmation
    is_valid, error = validate_password_match(
        data.get('password', ''),
        data.get('confirm_password', '')
    )
    if not is_valid:
        errors.append(error)
    
    # Names
    is_valid, error = validate_name(data.get('first_name', ''), "First name")
    if not is_valid:
        errors.append(error)
    
    is_valid, error = validate_name(data.get('last_name', ''), "Last name")
    if not is_valid:
        errors.append(error)
    
    return errors


def validate_book_data(data: dict) -> List[str]:
    """
    Validate book creation/update data.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # Required fields
    is_valid, error = validate_required(data.get('title', ''), "Title")
    if not is_valid:
        errors.append(error)
    
    is_valid, error = validate_required(data.get('author', ''), "Author")
    if not is_valid:
        errors.append(error)
    
    # ISBN (optional but must be valid if provided)
    isbn = data.get('isbn', '').strip()
    if isbn:
        is_valid, error = validate_isbn(isbn)
        if not is_valid:
            errors.append(f"ISBN: {error}")
    
    # Year (optional but must be reasonable if provided)
    year = data.get('year_published')
    if year:
        try:
            year_int = int(year)
            if year_int < 1000 or year_int > 2100:
                errors.append("Year must be between 1000 and 2100")
        except (ValueError, TypeError):
            errors.append("Year must be a number")
    
    return errors


def validate_inventory_data(data: dict) -> List[str]:
    """
    Validate inventory creation/update data.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # Book ID required
    is_valid, error = validate_uuid(data.get('book_id', ''), "Book ID")
    if not is_valid:
        errors.append(error)
    
    # Warehouse ID required
    is_valid, error = validate_uuid(data.get('warehouse_id', ''), "Warehouse ID")
    if not is_valid:
        errors.append(error)
    
    # Condition
    is_valid, error = validate_condition(data.get('condition'))
    if not is_valid:
        errors.append(f"Condition: {error}")
    
    # Quantity
    is_valid, error = validate_quantity(
        data.get('quantity', 0),
        "Quantity",
        min_value=0
    )
    if not is_valid:
        errors.append(error)
    
    # Prices
    is_valid, error = validate_money(data.get('acquisition_cost', '0'))
    if not is_valid:
        errors.append(f"Acquisition cost: {error}")
    
    is_valid, error = validate_money(data.get('list_price', '0'))
    if not is_valid:
        errors.append(f"List price: {error}")
    
    return errors


def validate_book_request_data(data: dict) -> List[str]:
    """
    Validate book request data.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # Title required
    is_valid, error = validate_required(data.get('title', ''), "Book title")
    if not is_valid:
        errors.append(error)
    
    # Author required
    is_valid, error = validate_required(data.get('author', ''), "Author")
    if not is_valid:
        errors.append(error)
    
    # Min condition
    is_valid, error = validate_condition(data.get('min_condition', 3))
    if not is_valid:
        errors.append(f"Minimum condition: {error}")
    
    # Max price (optional)
    max_price = data.get('max_price')
    if max_price:
        is_valid, error = validate_money(max_price, allow_zero=False)
        if not is_valid:
            errors.append(f"Maximum price: {error}")
    
    # ISBN (optional)
    isbn = data.get('isbn', '').strip()
    if isbn:
        is_valid, error = validate_isbn(isbn)
        if not is_valid:
            errors.append(f"ISBN: {error}")
    
    return errors
