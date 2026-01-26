// Healthcare Management System - JavaScript Functions

// Global variables
let loadingOverlay;

// Initialize on document ready
$(document).ready(function() {
    // Create loading overlay
    createLoadingOverlay();
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Initialize tooltips
    initializeTooltips();
    
    // Form validation
    validateForms();
});

// Create loading overlay
function createLoadingOverlay() {
    const overlay = $('<div class="spinner-overlay"><div class="spinner-border text-light" role="status"><span class="visually-hidden">Loading...</span></div></div>');
    $('body').append(overlay);
    loadingOverlay = overlay;
}

// Show loading spinner
function showLoading() {
    if (loadingOverlay) {
        loadingOverlay.addClass('show');
    }
}

// Hide loading spinner
function hideLoading() {
    if (loadingOverlay) {
        loadingOverlay.removeClass('show');
    }
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation
function validateForms() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Confirm action
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Show success message
function showSuccess(message) {
    showAlert(message, 'success');
}

// Show error message
function showError(message) {
    showAlert(message, 'danger');
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('.container').first().prepend(alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        $('.alert').first().fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Format time
function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showSuccess('Copied to clipboard!');
    }).catch(function(err) {
        showError('Failed to copy');
    });
}

// Debounce function
function debounce(func, wait) {
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

// AJAX request wrapper
function ajaxRequest(url, method = 'GET', data = null) {
    showLoading();
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .finally(() => {
            hideLoading();
        });
}

// Update medicine status
function updateMedicineStatus(logId, status) {
    ajaxRequest(`/patient/medicine/${logId}/taken`, 'POST')
        .then(data => {
            if (data.success) {
                showSuccess(data.message);
                location.reload();
            } else {
                showError(data.error || 'An error occurred');
            }
        })
        .catch(error => {
            showError('Failed to update medicine status');
            console.error('Error:', error);
        });
}

// Send emergency alert
function sendEmergencyAlert(message) {
    ajaxRequest('/patient/emergency', 'POST', { message: message })
        .then(data => {
            if (data.success) {
                showSuccess('Emergency alert sent to your caretaker!');
                $('#emergencyModal').modal('hide');
            } else {
                showError(data.error || 'Failed to send emergency alert');
            }
        })
        .catch(error => {
            showError('Failed to send emergency alert');
            console.error('Error:', error);
        });
}

// Request medicine reorder
function requestReorder(medicineId, quantity) {
    ajaxRequest(`/patient/reorder/${medicineId}`, 'POST', { quantity: quantity })
        .then(data => {
            if (data.success) {
                showSuccess('Reorder request sent to your caretaker!');
                $('#reorderModal').modal('hide');
            } else {
                showError(data.error || 'Failed to send reorder request');
            }
        })
        .catch(error => {
            showError('Failed to send reorder request');
            console.error('Error:', error);
        });
}

// Acknowledge emergency
function acknowledgeEmergency(alertId) {
    ajaxRequest(`/caretaker/emergency/${alertId}/acknowledge`, 'POST')
        .then(data => {
            if (data.success) {
                showSuccess('Emergency acknowledged');
                location.reload();
            } else {
                showError(data.error || 'Failed to acknowledge emergency');
            }
        })
        .catch(error => {
            showError('Failed to acknowledge emergency');
            console.error('Error:', error);
        });
}

// Resolve emergency
function resolveEmergency(alertId) {
    ajaxRequest(`/caretaker/emergency/${alertId}/resolve`, 'POST')
        .then(data => {
            if (data.success) {
                showSuccess('Emergency resolved');
                location.reload();
            } else {
                showError(data.error || 'Failed to resolve emergency');
            }
        })
        .catch(error => {
            showError('Failed to resolve emergency');
            console.error('Error:', error);
        });
}

// Process reorder request
function processReorder(reorderId, action) {
    ajaxRequest(`/caretaker/reorder/${reorderId}/process`, 'POST', { action: action })
        .then(data => {
            if (data.success) {
                showSuccess(`Reorder ${action}!`);
                location.reload();
            } else {
                showError(data.error || 'Failed to process reorder');
            }
        })
        .catch(error => {
            showError('Failed to process reorder');
            console.error('Error:', error);
        });
}

// Check for notifications (could be called periodically)
function checkNotifications() {
    // This would be implemented with WebSockets or polling
    // For now, it's a placeholder
    console.log('Checking for notifications...');
}

// Periodic notification check (every 30 seconds)
setInterval(checkNotifications, 30000);

// Service Worker registration for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // navigator.serviceWorker.register('/service-worker.js');
    });
}

// Export functions for global use
window.healthcareApp = {
    showLoading,
    hideLoading,
    showSuccess,
    showError,
    confirmAction,
    formatDate,
    formatTime,
    copyToClipboard,
    updateMedicineStatus,
    sendEmergencyAlert,
    requestReorder,
    acknowledgeEmergency,
    resolveEmergency,
    processReorder
};
