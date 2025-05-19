/**
 * JavaScript for the registration form
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form fields based on selected role
    const roleSelect = document.getElementById('role');
    if (roleSelect) {
        // Show fields immediately when role is selected
        roleSelect.addEventListener('change', function() {
            showRoleFields();
        });
        
        // Initialize on page load
        showRoleFields();
    }
});

/**
 * Show/hide fields based on selected role
 */
function showRoleFields() {
    const roleSelect = document.getElementById('role');
    const migrantFields = document.getElementById('migrantFields');
    const otherRoleFields = document.getElementById('otherRoleFields');
    const emailField = document.getElementById('emailField');
    
    if (!roleSelect) return;
    
    const selectedRole = roleSelect.value;
    
    // Hide all role-specific fields first
    if (migrantFields) migrantFields.style.display = 'none';
    if (otherRoleFields) otherRoleFields.style.display = 'none';
    
    // Show fields based on selected role
    if (selectedRole === 'migrant') {
        if (migrantFields) migrantFields.style.display = 'block';
        if (emailField) {
            const emailInput = document.getElementById('email');
            if (emailInput) emailInput.required = false;
        }
    } else if (selectedRole) { // Only show if a role is actually selected
        if (otherRoleFields) otherRoleFields.style.display = 'block';
        if (emailField) {
            const emailInput = document.getElementById('email');
            if (emailInput) emailInput.required = true;
        }
    }
}

/**
 * Toggle contact fields based on job info source
 */
function toggleContactFields() {
    const jobInfoSource = document.getElementById('job_info_source');
    const contactFields = document.querySelectorAll('.contact-fields');
    
    if (!jobInfoSource || !contactFields.length) return;
    
    const selectedSource = jobInfoSource.value;
    
    // Show contact fields only if 'friends' or 'agency' is selected
    const showFields = (selectedSource === 'friends' || selectedSource === 'agency');
    
    contactFields.forEach(field => {
        field.style.display = showFields ? 'block' : 'none';
        
        // Find input fields within this container and set required attribute
        const inputs = field.querySelectorAll('input');
        inputs.forEach(input => {
            input.required = showFields;
        });
    });
}

/**
 * Validate the registration form before submission
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            const roleSelect = document.getElementById('role');
            const selectedRole = roleSelect ? roleSelect.value : '';
            
            if (selectedRole === 'migrant') {
                // Validate migrant-specific fields
                const requiredFields = [
                    'name', 'mobile', 'dob', 'aadhar', 'current_address', 'current_city',
                    'native_state', 'native_address', 'job_info_source',
                    'contractor_name', 'contractor_number', 'company_name',
                    'company_type', 'company_sector'
                ];
                
                const jobInfoSource = document.getElementById('job_info_source');
                const selectedSource = jobInfoSource ? jobInfoSource.value : '';
                
                if (selectedSource === 'friends' || selectedSource === 'agency') {
                    requiredFields.push('contact_name', 'contact_number');
                }
                
                let isValid = true;
                
                requiredFields.forEach(fieldId => {
                    const field = document.getElementById(fieldId);
                    if (field && !field.value.trim()) {
                        field.classList.add('is-invalid');
                        isValid = false;
                    } else if (field) {
                        field.classList.remove('is-invalid');
                    }
                });
                
                if (!isValid) {
                    event.preventDefault();
                    alert('Please fill in all required fields');
                }
            }
        });
    }
});
