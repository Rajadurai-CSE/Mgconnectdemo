// MigrantConnect TN Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation
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

    // Job filter functionality
    const jobFilterForm = document.getElementById('job-filter-form');
    if (jobFilterForm) {
        jobFilterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const sector = document.getElementById('filter-sector').value;
            const location = document.getElementById('filter-location').value;
            
            // Make AJAX request to filter jobs
            fetch(`/filter-jobs?sector=${sector}&location=${location}`)
                .then(response => response.json())
                .then(data => {
                    updateJobsTable(data.jobs);
                })
                .catch(error => console.error('Error filtering jobs:', error));
        });
    }

    // Update jobs table with filtered results
    function updateJobsTable(jobs) {
        const jobsTableBody = document.getElementById('jobs-table-body');
        if (!jobsTableBody) return;

        // Clear existing rows
        jobsTableBody.innerHTML = '';

        if (jobs.length === 0) {
            // No jobs found message
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="5" class="text-center py-3">
                    <i class="fas fa-info-circle text-info"></i>
                    <p class="mb-0 mt-2">No jobs matching your filters were found.</p>
                </td>
            `;
            jobsTableBody.appendChild(row);
        } else {
            // Add job rows
            jobs.forEach(job => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${job.details.title}</td>
                    <td>${job.details.company_name}</td>
                    <td>${job.details.location}</td>
                    <td>${job.details.salary_range}</td>
                    <td>
                        <a href="/migrants/view-job/${job.job_id}" class="btn btn-sm btn-outline-primary">View</a>
                    </td>
                `;
                jobsTableBody.appendChild(row);
            });
        }
    }

    // File input preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const previewId = this.getAttribute('data-preview');
            if (!previewId) return;
            
            const preview = document.getElementById(previewId);
            if (!preview) return;
            
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    // Show loading spinner on form submission
    const submitForms = document.querySelectorAll('form[data-loading="true"]');
    submitForms.forEach(form => {
        form.addEventListener('submit', function() {
            // Create spinner overlay
            const spinner = document.createElement('div');
            spinner.className = 'spinner-overlay';
            spinner.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            `;
            document.body.appendChild(spinner);
        });
    });

    // Skills and languages input enhancement
    const enhanceMultiInputs = () => {
        const multiInputs = document.querySelectorAll('[data-role="multi-input"]');
        multiInputs.forEach(input => {
            // Create a hidden input to store the actual comma-separated values
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = input.name;
            input.removeAttribute('name');
            input.parentNode.appendChild(hiddenInput);
            
            // Create a container for the tags
            const tagsContainer = document.createElement('div');
            tagsContainer.className = 'tags-container d-flex flex-wrap gap-1 mt-2';
            input.parentNode.insertBefore(tagsContainer, input.nextSibling);
            
            // Function to update hidden input value
            const updateHiddenInput = () => {
                const tags = Array.from(tagsContainer.querySelectorAll('.tag-item')).map(tag => tag.textContent.trim());
                hiddenInput.value = tags.join(',');
            };
            
            // Function to add a new tag
            const addTag = (value) => {
                if (!value.trim()) return;
                
                const tag = document.createElement('span');
                tag.className = 'tag-item badge bg-primary me-1 mb-1';
                tag.textContent = value.trim();
                
                const removeBtn = document.createElement('span');
                removeBtn.className = 'ms-1 cursor-pointer';
                removeBtn.innerHTML = '&times;';
                removeBtn.onclick = function() {
                    tagsContainer.removeChild(tag);
                    updateHiddenInput();
                };
                
                tag.appendChild(removeBtn);
                tagsContainer.appendChild(tag);
                input.value = '';
                updateHiddenInput();
            };
            
            // Handle input events
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ',') {
                    e.preventDefault();
                    addTag(this.value);
                }
            });
            
            input.addEventListener('blur', function() {
                if (this.value.trim()) {
                    addTag(this.value);
                }
            });
            
            // Initialize with existing values if any
            if (input.value) {
                input.value.split(',').forEach(val => {
                    if (val.trim()) addTag(val.trim());
                });
                input.value = '';
            }
        });
    };
    
    enhanceMultiInputs();
});
