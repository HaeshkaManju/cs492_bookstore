"""
API Hooks Tests
===============

Tests for the hook system used by RBAC integration.
"""

import pytest
from app.api.hooks import (
    register_permission_hook,
    register_audit_hook,
    register_event_hook,
    check_permission,
    audit,
    emit_event,
    clear_all_hooks,
    has_permission_hook,
    has_audit_hook,
    get_registered_events,
    EVENT_BOOK_CREATED,
    EVENT_INVENTORY_LOW_STOCK
)


class TestPermissionHooks:
    """Tests for permission checking hooks."""
    
    def setup_method(self):
        """Clear hooks before each test."""
        clear_all_hooks()
    
    def teardown_method(self):
        """Clear hooks after each test."""
        clear_all_hooks()
    
    def test_no_hook_allows_all(self):
        """Without hook registered, all permissions are allowed."""
        assert check_permission(None, 'anything') is True
        assert check_permission('user', 'manage_inventory') is True
    
    def test_register_permission_hook(self):
        """Test registering a permission hook."""
        assert has_permission_hook() is False
        
        def my_hook(user, permission):
            return user == 'admin'
        
        register_permission_hook(my_hook)
        
        assert has_permission_hook() is True
    
    def test_permission_hook_called(self):
        """Test that registered hook is called."""
        calls = []
        
        def tracking_hook(user, permission):
            calls.append((user, permission))
            return True
        
        register_permission_hook(tracking_hook)
        
        check_permission('user123', 'view_inventory')
        
        assert len(calls) == 1
        assert calls[0] == ('user123', 'view_inventory')
    
    def test_permission_hook_denies(self):
        """Test that hook can deny permission."""
        def deny_all(user, permission):
            return False
        
        register_permission_hook(deny_all)
        
        assert check_permission('admin', 'anything') is False
    
    def test_permission_hook_role_based(self):
        """Test role-based permission checking."""
        class FakeUser:
            def __init__(self, role):
                self.role = role
        
        def role_check(user, permission):
            if user is None:
                return False
            if user.role == 'admin':
                return True
            if user.role == 'employee' and permission.startswith('view_'):
                return True
            return False
        
        register_permission_hook(role_check)
        
        admin = FakeUser('admin')
        employee = FakeUser('employee')
        
        assert check_permission(admin, 'delete_everything') is True
        assert check_permission(employee, 'view_inventory') is True
        assert check_permission(employee, 'delete_inventory') is False
        assert check_permission(None, 'view_inventory') is False


class TestAuditHooks:
    """Tests for audit logging hooks."""
    
    def setup_method(self):
        clear_all_hooks()
    
    def teardown_method(self):
        clear_all_hooks()
    
    def test_no_hook_does_nothing(self):
        """Without hook, audit does nothing."""
        # Should not raise
        audit('some.action', user=None, detail='test')
    
    def test_register_audit_hook(self):
        """Test registering audit hook."""
        assert has_audit_hook() is False
        
        def my_audit(action, user, details):
            pass
        
        register_audit_hook(my_audit)
        
        assert has_audit_hook() is True
    
    def test_audit_hook_called(self):
        """Test that audit hook is called with correct args."""
        logs = []
        
        def capture_audit(action, user, details):
            logs.append({
                'action': action,
                'user': user,
                'details': details
            })
        
        register_audit_hook(capture_audit)
        
        audit('invoice.sent', user='user1', invoice_id='123', total='99.99')
        
        assert len(logs) == 1
        assert logs[0]['action'] == 'invoice.sent'
        assert logs[0]['user'] == 'user1'
        assert logs[0]['details']['invoice_id'] == '123'
        assert logs[0]['details']['total'] == '99.99'


class TestEventHooks:
    """Tests for event system hooks."""
    
    def setup_method(self):
        clear_all_hooks()
    
    def teardown_method(self):
        clear_all_hooks()
    
    def test_no_hooks_for_event(self):
        """Events with no hooks do nothing."""
        # Should not raise
        emit_event('nonexistent.event', data='test')
    
    def test_register_event_hook(self):
        """Test registering event hook."""
        def handler(data):
            pass
        
        register_event_hook(EVENT_BOOK_CREATED, handler)
        
        assert EVENT_BOOK_CREATED in get_registered_events()
    
    def test_event_hook_called(self):
        """Test that event hook is called."""
        received = []
        
        def handler(data):
            received.append(data)
        
        register_event_hook(EVENT_BOOK_CREATED, handler)
        
        emit_event(EVENT_BOOK_CREATED, book_id='123', title='Test Book')
        
        assert len(received) == 1
        assert received[0]['book_id'] == '123'
        assert received[0]['title'] == 'Test Book'
    
    def test_multiple_handlers_same_event(self):
        """Test multiple handlers for same event."""
        calls = {'handler1': 0, 'handler2': 0}
        
        def handler1(data):
            calls['handler1'] += 1
        
        def handler2(data):
            calls['handler2'] += 1
        
        register_event_hook(EVENT_INVENTORY_LOW_STOCK, handler1)
        register_event_hook(EVENT_INVENTORY_LOW_STOCK, handler2)
        
        emit_event(EVENT_INVENTORY_LOW_STOCK, inventory_id='abc')
        
        assert calls['handler1'] == 1
        assert calls['handler2'] == 1
    
    def test_different_events_different_handlers(self):
        """Test that handlers are event-specific."""
        book_events = []
        inventory_events = []
        
        def book_handler(data):
            book_events.append(data)
        
        def inventory_handler(data):
            inventory_events.append(data)
        
        register_event_hook(EVENT_BOOK_CREATED, book_handler)
        register_event_hook(EVENT_INVENTORY_LOW_STOCK, inventory_handler)
        
        emit_event(EVENT_BOOK_CREATED, book_id='1')
        emit_event(EVENT_INVENTORY_LOW_STOCK, inventory_id='2')
        
        assert len(book_events) == 1
        assert book_events[0]['book_id'] == '1'
        
        assert len(inventory_events) == 1
        assert inventory_events[0]['inventory_id'] == '2'


class TestClearHooks:
    """Tests for clearing hooks."""
    
    def test_clear_all_hooks(self):
        """Test that clear_all_hooks clears everything."""
        # Register hooks
        register_permission_hook(lambda u, p: True)
        register_audit_hook(lambda a, u, d: None)
        register_event_hook(EVENT_BOOK_CREATED, lambda d: None)
        
        # Verify registered
        assert has_permission_hook() is True
        assert has_audit_hook() is True
        assert len(get_registered_events()) == 1
        
        # Clear
        clear_all_hooks()
        
        # Verify cleared
        assert has_permission_hook() is False
        assert has_audit_hook() is False
        assert len(get_registered_events()) == 0
