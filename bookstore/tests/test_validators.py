"""
Validator Tests
===============

Tests for input validation functions.
"""

import pytest
from decimal import Decimal

from app.utils.validators import (
    validate_email,
    validate_password,
    validate_isbn,
    validate_isbn10,
    validate_isbn13,
    validate_phone,
    validate_money,
    validate_condition,
    validate_quantity,
    validate_required,
    validate_length,
    validate_range,
    ValidationError,
    CONDITION_LABELS
)


class TestEmailValidation:
    """Tests for email validation."""
    
    def test_valid_emails(self):
        """Test valid email formats."""
        valid_emails = [
            'user@example.com',
            'user.name@example.com',
            'user+tag@example.com',
            'user@subdomain.example.com',
            'user123@example.co.uk',
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True, f"Should be valid: {email}"
    
    def test_invalid_emails(self):
        """Test invalid email formats."""
        invalid_emails = [
            '',
            'notanemail',
            '@nodomain.com',
            'no@domain',
            'spaces in@email.com',
            'no@spaces .com',
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False, f"Should be invalid: {email}"
    
    def test_none_email(self):
        """Test None email."""
        assert validate_email(None) is False


class TestPasswordValidation:
    """Tests for password validation."""
    
    def test_valid_passwords(self):
        """Test valid passwords."""
        valid_passwords = [
            'SecurePass123!',
            'MyP@ssw0rd',
            'Abcd1234!@#$',
            'VeryLongSecurePassword1!',
        ]
        
        for password in valid_passwords:
            errors = validate_password(password)
            assert len(errors) == 0, f"Should be valid: {password}, errors: {errors}"
    
    def test_too_short(self):
        """Test password too short."""
        errors = validate_password('Ab1!')
        assert any('8 characters' in e for e in errors)
    
    def test_no_uppercase(self):
        """Test password without uppercase."""
        errors = validate_password('lowercase123!')
        assert any('uppercase' in e.lower() for e in errors)
    
    def test_no_lowercase(self):
        """Test password without lowercase."""
        errors = validate_password('UPPERCASE123!')
        assert any('lowercase' in e.lower() for e in errors)
    
    def test_no_digit(self):
        """Test password without digit."""
        errors = validate_password('NoDigitsHere!')
        assert any('digit' in e.lower() or 'number' in e.lower() for e in errors)
    
    def test_no_special(self):
        """Test password without special character."""
        errors = validate_password('NoSpecial123')
        assert any('special' in e.lower() for e in errors)
    
    def test_none_password(self):
        """Test None password."""
        errors = validate_password(None)
        assert len(errors) > 0


class TestISBNValidation:
    """Tests for ISBN validation."""
    
    def test_valid_isbn10(self):
        """Test valid ISBN-10."""
        valid_isbns = [
            '0-306-40615-2',
            '0306406152',
            '0-596-52068-9',
        ]
        
        for isbn in valid_isbns:
            assert validate_isbn10(isbn) is True, f"Should be valid ISBN-10: {isbn}"
    
    def test_valid_isbn13(self):
        """Test valid ISBN-13."""
        valid_isbns = [
            '978-0-306-40615-7',
            '9780306406157',
            '978-3-16-148410-0',
        ]
        
        for isbn in valid_isbns:
            assert validate_isbn13(isbn) is True, f"Should be valid ISBN-13: {isbn}"
    
    def test_validate_isbn_accepts_both(self):
        """Test validate_isbn accepts both formats."""
        assert validate_isbn('0-306-40615-2') is True  # ISBN-10
        assert validate_isbn('978-0-306-40615-7') is True  # ISBN-13
    
    def test_invalid_isbns(self):
        """Test invalid ISBNs."""
        invalid_isbns = [
            '123456789',  # Too short
            '12345678901234',  # Too long
            'not-an-isbn',
            '978-0-306-40615-X',  # Invalid ISBN-13 check digit
        ]
        
        for isbn in invalid_isbns:
            assert validate_isbn(isbn) is False, f"Should be invalid: {isbn}"
    
    def test_none_isbn(self):
        """Test None ISBN is valid (ISBN is optional)."""
        assert validate_isbn(None) is True
    
    def test_empty_isbn(self):
        """Test empty ISBN is valid (ISBN is optional)."""
        assert validate_isbn('') is True


class TestPhoneValidation:
    """Tests for phone validation."""
    
    def test_valid_phones(self):
        """Test valid phone formats."""
        valid_phones = [
            '555-1234',
            '(555) 123-4567',
            '+1-555-123-4567',
            '5551234567',
            '+44 20 7123 4567',
        ]
        
        for phone in valid_phones:
            assert validate_phone(phone) is True, f"Should be valid: {phone}"
    
    def test_invalid_phones(self):
        """Test invalid phone formats."""
        invalid_phones = [
            '123',  # Too short
            'not-a-phone',
            'abc-def-ghij',
        ]
        
        for phone in invalid_phones:
            assert validate_phone(phone) is False, f"Should be invalid: {phone}"
    
    def test_none_phone(self):
        """Test None phone is valid (phone is optional)."""
        assert validate_phone(None) is True


class TestMoneyValidation:
    """Tests for money/decimal validation."""
    
    def test_valid_amounts(self):
        """Test valid money amounts."""
        valid_amounts = [
            Decimal('0.00'),
            Decimal('1.00'),
            Decimal('99.99'),
            Decimal('1000.00'),
            Decimal('0.01'),
        ]
        
        for amount in valid_amounts:
            assert validate_money(amount) is True, f"Should be valid: {amount}"
    
    def test_negative_amount(self):
        """Test negative amount is invalid."""
        assert validate_money(Decimal('-1.00')) is False
    
    def test_none_amount(self):
        """Test None amount."""
        assert validate_money(None) is False
    
    def test_string_amount(self):
        """Test string amount."""
        assert validate_money('10.00') is False
    
    def test_float_amount(self):
        """Test float amount (should use Decimal)."""
        assert validate_money(10.00) is False


class TestConditionValidation:
    """Tests for book condition validation."""
    
    def test_valid_conditions(self):
        """Test valid condition values (1-5)."""
        for condition in [1, 2, 3, 4, 5]:
            assert validate_condition(condition) is True, f"Should be valid: {condition}"
    
    def test_invalid_conditions(self):
        """Test invalid condition values."""
        invalid = [0, 6, -1, 10, 2.5]
        
        for condition in invalid:
            assert validate_condition(condition) is False, f"Should be invalid: {condition}"
    
    def test_none_condition(self):
        """Test None condition."""
        assert validate_condition(None) is False


class TestQuantityValidation:
    """Tests for quantity validation."""
    
    def test_valid_quantities(self):
        """Test valid quantity values."""
        valid = [0, 1, 10, 100, 1000]
        
        for qty in valid:
            assert validate_quantity(qty) is True, f"Should be valid: {qty}"
    
    def test_negative_quantity(self):
        """Test negative quantity is invalid."""
        assert validate_quantity(-1) is False
    
    def test_float_quantity(self):
        """Test float quantity is invalid."""
        assert validate_quantity(1.5) is False
    
    def test_none_quantity(self):
        """Test None quantity."""
        assert validate_quantity(None) is False


class TestRequiredValidation:
    """Tests for required field validation."""
    
    def test_valid_values(self):
        """Test non-empty values are valid."""
        valid = ['text', 123, ['list'], {'dict': 'value'}, True]
        
        for value in valid:
            assert validate_required(value) is True, f"Should be valid: {value}"
    
    def test_invalid_values(self):
        """Test empty values are invalid."""
        invalid = [None, '', '   ', [], {}]
        
        for value in invalid:
            assert validate_required(value) is False, f"Should be invalid: {value}"


class TestLengthValidation:
    """Tests for length validation."""
    
    def test_within_range(self):
        """Test string within length range."""
        assert validate_length('hello', min_len=1, max_len=10) is True
        assert validate_length('abc', min_len=3, max_len=3) is True
    
    def test_too_short(self):
        """Test string too short."""
        assert validate_length('ab', min_len=3) is False
    
    def test_too_long(self):
        """Test string too long."""
        assert validate_length('abcdefghijk', max_len=10) is False
    
    def test_none_length(self):
        """Test None value."""
        assert validate_length(None, min_len=1) is False


class TestRangeValidation:
    """Tests for numeric range validation."""
    
    def test_within_range(self):
        """Test value within range."""
        assert validate_range(5, min_val=1, max_val=10) is True
        assert validate_range(1, min_val=1, max_val=10) is True
        assert validate_range(10, min_val=1, max_val=10) is True
    
    def test_below_min(self):
        """Test value below minimum."""
        assert validate_range(0, min_val=1) is False
    
    def test_above_max(self):
        """Test value above maximum."""
        assert validate_range(11, max_val=10) is False
    
    def test_none_value(self):
        """Test None value."""
        assert validate_range(None, min_val=1, max_val=10) is False


class TestValidationError:
    """Tests for ValidationError exception."""
    
    def test_single_error(self):
        """Test ValidationError with single error."""
        error = ValidationError(['Field is required'])
        
        assert len(error.errors) == 1
        assert 'Field is required' in str(error)
    
    def test_multiple_errors(self):
        """Test ValidationError with multiple errors."""
        errors = [
            'Email is invalid',
            'Password is too short',
            'Name is required'
        ]
        error = ValidationError(errors)
        
        assert len(error.errors) == 3
        for e in errors:
            assert e in error.errors
    
    def test_empty_errors(self):
        """Test ValidationError with empty list."""
        error = ValidationError([])
        assert len(error.errors) == 0
