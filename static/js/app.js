// Global variables
let templates = [];
let schools = [];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get data from server
    const templateSelect = document.getElementById('templateSelect');
    if (templateSelect) {
        templates = Array.from(templateSelect.options).slice(1).map(option => ({
            id: parseInt(option.value),
            name: option.text
        }));
    }

    // Handle A/B testing checkbox
    const abTestingCheckbox = document.getElementById('abTesting');
    if (abTestingCheckbox) {
        abTestingCheckbox.addEventListener('change', function() {
            const templateSelect = document.getElementById('templateSelect');
            if (this.checked) {
                templateSelect.disabled = true;
                templateSelect.value = '';
            } else {
                templateSelect.disabled = false;
            }
        });
    }
});

// Toggle select all functionality
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const schoolCheckboxes = document.querySelectorAll('.school-checkbox');
    
    schoolCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
}

// Select all schools
function selectAllSchools() {
    const schoolCheckboxes = document.querySelectorAll('.school-checkbox');
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    
    schoolCheckboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
    
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = true;
    }
}

// Clear selection
function clearSelection() {
    const schoolCheckboxes = document.querySelectorAll('.school-checkbox');
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    
    schoolCheckboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = false;
    }
}

// Get selected school indices
function getSelectedSchools() {
    const selectedSchools = [];
    const schoolCheckboxes = document.querySelectorAll('.school-checkbox:checked');
    
    schoolCheckboxes.forEach(checkbox => {
        selectedSchools.push(parseInt(checkbox.value));
    });
    
    return selectedSchools;
}

// Preview email
async function previewEmail() {
    const templateSelect = document.getElementById('templateSelect');
    const abTesting = document.getElementById('abTesting').checked;
    const customContent = document.getElementById('customContent').value;
    const customSubject = document.getElementById('customSubject').value;
    const customHtmlContent = document.getElementById('customHtmlContent').value;
    
    if (!abTesting && !templateSelect.value && !customContent && !customHtmlContent) {
        alert('Please select a template or enter custom content');
        return;
    }
    
    const selectedSchools = getSelectedSchools();
    if (selectedSchools.length === 0) {
        alert('Please select at least one school');
        return;
    }
    
    // Use first selected school for preview
    const schoolIndex = selectedSchools[0];
    
    try {
        const response = await fetch('/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                template_id: parseInt(templateSelect.value),
                school_index: schoolIndex,
                custom_content: customContent || null,
                custom_subject: customSubject || null,
                custom_html_content: customHtmlContent || null
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Show preview in modal
            document.getElementById('previewTo').textContent = data.school.Email;
            document.getElementById('previewSubject').textContent = data.subject;
            
            // Use HTML content if available, otherwise plain text
            const contentElement = document.getElementById('previewContent');
            if (data.html_content && data.html_content.trim()) {
                contentElement.innerHTML = data.html_content;
            } else {
                contentElement.innerHTML = '<pre style="white-space: pre-wrap; font-family: inherit;">' + data.content + '</pre>';
            }
            
            const modal = new bootstrap.Modal(document.getElementById('previewModal'));
            modal.show();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error previewing email:', error);
        alert('Error previewing email: ' + error.message);
    }
}

// Send test email with current form content
async function sendTestEmail() {
    const templateSelect = document.getElementById('templateSelect');
    const customSubject = document.getElementById('customSubject').value;
    const customContent = document.getElementById('customContent').value;
    const customHtmlContent = document.getElementById('customHtmlContent').value;
    
    if (!confirm('Send test email with current content to rishulchanana36@gmail.com?')) {
        return;
    }
    
    try {
        const response = await fetch('/send_test_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                template_id: parseInt(templateSelect.value) || null,
                subject: customSubject,
                content: customContent,
                html_content: customHtmlContent
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✅ Test email sent successfully to rishulchanana36@gmail.com!');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error sending test email:', error);
        alert('Error sending test email: ' + error.message);
    }
}

// Delete template
function deleteTemplate(templateId, templateName) {
    if (!confirm(`Are you sure you want to delete template "${templateName}"? This action cannot be undone.`)) {
        return;
    }
    
    // Create a form and submit it for deletion
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/delete_template/${templateId}`;
    document.body.appendChild(form);
    form.submit();
}

// Send custom email without templates
async function sendCustomEmail() {
    const customSubject = document.getElementById('customSubject').value;
    const customContent = document.getElementById('customContent').value;
    const customHtmlContent = document.getElementById('customHtmlContent').value;
    
    if (!customSubject || (!customContent && !customHtmlContent)) {
        alert('Please enter a subject and content for your custom email');
        return;
    }
    
    const selectedSchools = getSelectedSchools();
    if (selectedSchools.length === 0) {
        alert('Please select at least one school');
        return;
    }
    
    // Confirm sending
    const confirmMessage = `Send custom email to ${selectedSchools.length} school(s)?`;
    if (!confirm(confirmMessage)) {
        return;
    }
    
    // Show loading modal
    showLoadingModal('Preparing custom email...', selectedSchools.length);
    
    try {
        const response = await fetch('/send_custom_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                subject: customSubject,
                content: customContent,
                html_content: customHtmlContent,
                selected_schools: selectedSchools
            })
        });
        
        const data = await response.json();
        updateLoadingProgress('Custom emails sent successfully!', 100);
        
        if (response.ok) {
            // Show results with animated success
            let successCount = 0;
            let errorCount = 0;
            
            data.results.forEach(result => {
                if (result.status === 'success') {
                    successCount++;
                } else {
                    errorCount++;
                }
            });
            
            // Hide loading modal and show results
            setTimeout(() => {
                hideLoadingModal();
                showResultsModal('Custom email sending completed!', successCount, errorCount);
                
                // Reload page after showing results
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            }, 1000);
        } else {
            hideLoadingModal();
            showErrorModal('Error: ' + data.error);
        }
    } catch (error) {
        hideLoadingModal();
        console.error('Error sending custom emails:', error);
        showErrorModal('Error sending custom emails: ' + error.message);
    }
}

// Send emails
async function sendEmails() {
    const templateSelect = document.getElementById('templateSelect');
    const abTesting = document.getElementById('abTesting').checked;
    const customContent = document.getElementById('customContent').value;
    const customSubject = document.getElementById('customSubject').value;
    const sendButton = document.getElementById('sendButton');
    
    const selectedSchools = getSelectedSchools();
    if (selectedSchools.length === 0) {
        alert('Please select at least one school');
        return;
    }
    
    if (!abTesting && !templateSelect.value) {
        alert('Please select a template or enable A/B testing');
        return;
    }
    
    // Confirm sending
    const confirmMessage = `Are you sure you want to send emails to ${selectedSchools.length} school(s)?`;
    if (!confirm(confirmMessage)) {
        return;
    }
    
    // Show loading modal
    showLoadingModal('Preparing to send emails...', selectedSchools.length);
    
    // Disable send button and show loading
    sendButton.disabled = true;
    sendButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Sending...';
    
    // Create an AbortController for request timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
    
    try {
        const response = await fetch('/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                template_id: parseInt(templateSelect.value),
                selected_schools: selectedSchools,
                ab_testing: abTesting,
                custom_content: customContent || null,
                custom_subject: customSubject || null,
                custom_html_content: document.getElementById('customHtmlContent').value || null
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        updateLoadingProgress('Processing response...', 90);
        
        if (!response.ok) {
            hideLoadingModal();
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        updateLoadingProgress('Emails sent successfully!', 100);
        
        // Show results with animated success
        let successCount = 0;
        let errorCount = 0;
        
        if (data.results && Array.isArray(data.results)) {
            data.results.forEach(result => {
                if (result.status === 'success') {
                    successCount++;
                } else {
                    errorCount++;
                }
            });
        }
        
        // Hide loading modal and show results
        setTimeout(() => {
            hideLoadingModal();
            
            let message = `Email sending completed!\n`;
            message += `✅ Successful: ${successCount}\n`;
            if (errorCount > 0) {
                message += `❌ Errors: ${errorCount}\n`;
            }
            if (data.removed_schools > 0) {
                message += `🗑️ Removed ${data.removed_schools} school(s) from list`;
            }
            
            showResultsModal(message, successCount, errorCount);
            
            // Reload page after showing results
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        }, 1000);
        
    } catch (error) {
        clearTimeout(timeoutId);
        hideLoadingModal();
        console.error('Error sending emails:', error);
        
        let errorMessage = 'Error sending emails: ';
        if (error.name === 'AbortError') {
            errorMessage += 'Request timed out. The operation may still be running in the background.';
        } else if (error.message) {
            errorMessage += error.message;
        } else {
            errorMessage += 'Unknown error occurred';
        }
        
        showErrorModal(errorMessage);
    } finally {
        // Re-enable send button
        sendButton.disabled = false;
        sendButton.innerHTML = '<i class="bi bi-send"></i> Send with Template';
    }
}

// Update individual checkboxes when clicked
document.addEventListener('change', function(e) {
    if (e.target.classList.contains('school-checkbox')) {
        updateSelectAllCheckbox();
    }
});

// Update select all checkbox based on individual checkboxes
function updateSelectAllCheckbox() {
    const schoolCheckboxes = document.querySelectorAll('.school-checkbox');
    const checkedCheckboxes = document.querySelectorAll('.school-checkbox:checked');
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    
    if (selectAllCheckbox) {
        if (checkedCheckboxes.length === 0) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = false;
        } else if (checkedCheckboxes.length === schoolCheckboxes.length) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = true;
        } else {
            selectAllCheckbox.indeterminate = true;
        }
    }
}

// Loading Modal Functions
function showLoadingModal(message, totalEmails) {
    const modalHtml = `
        <div class="modal fade" id="loadingModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-body text-center py-4">
                        <div class="mb-3">
                            <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                        <h5 id="loadingMessage">${message}</h5>
                        <p class="text-muted mb-3">Sending to ${totalEmails} school(s)</p>
                        <div class="progress mb-2" style="height: 8px;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                 id="loadingProgress" role="progressbar" style="width: 10%"></div>
                        </div>
                        <small class="text-muted" id="progressText">Starting...</small>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('loadingModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
    
    // Start progress animation
    animateProgress();
}

function updateLoadingProgress(message, percentage) {
    const loadingMessage = document.getElementById('loadingMessage');
    const progressBar = document.getElementById('loadingProgress');
    const progressText = document.getElementById('progressText');
    
    if (loadingMessage) loadingMessage.textContent = message;
    if (progressBar) progressBar.style.width = percentage + '%';
    if (progressText) progressText.textContent = `${percentage}% complete`;
}

function animateProgress() {
    let progress = 10;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 85) {
            clearInterval(interval);
            return;
        }
        
        const progressBar = document.getElementById('loadingProgress');
        const progressText = document.getElementById('progressText');
        if (progressBar) progressBar.style.width = progress + '%';
        if (progressText) progressText.textContent = `${Math.round(progress)}% complete`;
    }, 1000);
}

function hideLoadingModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
    if (modal) {
        modal.hide();
        setTimeout(() => {
            const modalElement = document.getElementById('loadingModal');
            if (modalElement) modalElement.remove();
        }, 300);
    }
}

function showResultsModal(message, successCount, errorCount) {
    const iconClass = errorCount > 0 ? 'bi-exclamation-triangle text-warning' : 'bi-check-circle text-success';
    const title = errorCount > 0 ? 'Partially Complete' : 'Success!';
    
    const modalHtml = `
        <div class="modal fade" id="resultsModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0 text-center">
                        <div class="w-100">
                            <i class="bi ${iconClass}" style="font-size: 3rem;"></i>
                            <h4 class="modal-title mt-2">${title}</h4>
                        </div>
                    </div>
                    <div class="modal-body text-center">
                        <div class="row">
                            <div class="col-6">
                                <div class="p-3 bg-success bg-opacity-10 rounded">
                                    <h3 class="text-success mb-0">${successCount}</h3>
                                    <small class="text-muted">Sent Successfully</small>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="p-3 ${errorCount > 0 ? 'bg-warning bg-opacity-10' : 'bg-light'} rounded">
                                    <h3 class="${errorCount > 0 ? 'text-warning' : 'text-muted'} mb-0">${errorCount}</h3>
                                    <small class="text-muted">Errors</small>
                                </div>
                            </div>
                        </div>
                        ${errorCount > 0 ? '<p class="mt-3 text-muted">Check the Error Dashboard for details</p>' : ''}
                    </div>
                    <div class="modal-footer border-0 justify-content-center">
                        <small class="text-muted">Page will refresh automatically...</small>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('resultsModal'));
    modal.show();
}

function showErrorModal(errorMessage) {
    const modalHtml = `
        <div class="modal fade" id="errorModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0 text-center">
                        <div class="w-100">
                            <i class="bi bi-x-circle text-danger" style="font-size: 3rem;"></i>
                            <h4 class="modal-title mt-2">Error Occurred</h4>
                        </div>
                    </div>
                    <div class="modal-body text-center">
                        <p class="text-muted">${errorMessage}</p>
                    </div>
                    <div class="modal-footer border-0 justify-content-center">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('errorModal'));
    modal.show();
}
