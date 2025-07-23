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
        
        if (response.ok) {
            // Show results
            let successCount = 0;
            let errorCount = 0;
            
            data.results.forEach(result => {
                if (result.status === 'success') {
                    successCount++;
                } else {
                    errorCount++;
                }
            });
            
            let message = `Custom email sending completed!\n`;
            message += `✅ Successful: ${successCount}\n`;
            if (errorCount > 0) {
                message += `❌ Errors: ${errorCount}`;
            }
            
            alert(message);
            
            // Reload page to show updated logs
            window.location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error sending custom emails:', error);
        alert('Error sending custom emails: ' + error.message);
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
    
    // Disable send button and show loading
    sendButton.disabled = true;
    sendButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Sending...';
    
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
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Show results
            let successCount = 0;
            let errorCount = 0;
            
            data.results.forEach(result => {
                if (result.status === 'success') {
                    successCount++;
                } else {
                    errorCount++;
                }
            });
            
            let message = `Email sending completed!\n`;
            message += `✅ Successful: ${successCount}\n`;
            if (errorCount > 0) {
                message += `❌ Errors: ${errorCount}`;
            }
            
            alert(message);
            
            // Reload page to show updated logs
            window.location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error sending emails:', error);
        alert('Error sending emails: ' + error.message);
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
