/**
 * Bookstore Inventory Management System
 * Custom JavaScript
 * ============================================
 */

'use strict';

/* -----------------------------------------------------------------------------
   DOM Ready Handler
   ----------------------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize auto-dismiss alerts
    initAutoDismissAlerts();
    
    // Initialize confirmation dialogs
    initConfirmationDialogs();
});

/* -----------------------------------------------------------------------------
   Bootstrap Tooltips
   ----------------------------------------------------------------------------- */

function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/* -----------------------------------------------------------------------------
   Auto-dismiss Alerts
   ----------------------------------------------------------------------------- */

function initAutoDismissAlerts() {
    // Auto-dismiss success and info alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-success, .alert-info');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
}

/* -----------------------------------------------------------------------------
   Confirmation Dialogs
   ----------------------------------------------------------------------------- */

function initConfirmationDialogs() {
    // Add confirmation to dangerous actions
    document.querySelectorAll('[data-confirm]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

/* -----------------------------------------------------------------------------
   Form Helpers
   ----------------------------------------------------------------------------- */

/**
 * Clear all form fields
 * @param {HTMLFormElement} form - The form to clear
 */
function clearForm(form) {
    form.reset();
    // Clear any validation state
    form.querySelectorAll('.is-invalid').forEach(function(el) {
        el.classList.remove('is-invalid');
    });
    form.querySelectorAll('.invalid-feedback').forEach(function(el) {
        el.textContent = '';
    });
}

/**
 * Disable/enable form submission
 * @param {HTMLFormElement} form - The form
 * @param {boolean} disabled - Whether to disable
 */
function setFormDisabled(form, disabled) {
    const submitBtns = form.querySelectorAll('button[type="submit"], input[type="submit"]');
    submitBtns.forEach(function(btn) {
        btn.disabled = disabled;
        if (disabled) {
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
        } else if (btn.dataset.originalText) {
            btn.innerHTML = btn.dataset.originalText;
        }
    });
}

/* -----------------------------------------------------------------------------
   Currency Formatting
   ----------------------------------------------------------------------------- */

/**
 * Format a number as currency
 * @param {number} amount - The amount to format
 * @param {string} currency - Currency code (default: USD)
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/* -----------------------------------------------------------------------------
   Condition Helpers
   ----------------------------------------------------------------------------- */

const CONDITION_LABELS = {
    5: 'Fine',
    4: 'Very Good',
    3: 'Good',
    2: 'Fair',
    1: 'Poor'
};

const CONDITION_CLASSES = {
    5: 'badge-condition-fine',
    4: 'badge-condition-very-good',
    3: 'badge-condition-good',
    2: 'badge-condition-fair',
    1: 'badge-condition-poor'
};

/**
 * Get condition label from value
 * @param {number} condition - Condition value (1-5)
 * @returns {string} Condition label
 */
function getConditionLabel(condition) {
    return CONDITION_LABELS[condition] || 'Unknown';
}

/**
 * Get condition badge class from value
 * @param {number} condition - Condition value (1-5)
 * @returns {string} CSS class for badge
 */
function getConditionClass(condition) {
    return CONDITION_CLASSES[condition] || '';
}

/* -----------------------------------------------------------------------------
   Search/Filter Helpers
   ----------------------------------------------------------------------------- */

/**
 * Debounce function for search inputs
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
