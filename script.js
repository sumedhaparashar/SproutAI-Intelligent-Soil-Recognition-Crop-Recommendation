document.addEventListener('DOMContentLoaded', function() {
    // Image preview functionality
    const fileInput = document.getElementById('soil_image');
    const imagePreview = document.getElementById('imagePreview');
    const preview = document.getElementById('preview');
    const uploadForm = document.getElementById('uploadForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            
            // Clear previous preview
            if (!file) {
                imagePreview.classList.add('d-none');
                return;
            }

            // Check file type
            const fileType = file.type;
            if (!fileType.match('image/jpeg') && !fileType.match('image/png') && !fileType.match('image/jpg')) {
                alert('Please select a valid image file (JPEG, JPG, or PNG)');
                fileInput.value = '';
                imagePreview.classList.add('d-none');
                return;
            }

            // Check file size (max 16MB)
            if (file.size > 16 * 1024 * 1024) {
                alert('File is too large! Maximum file size is 16MB.');
                fileInput.value = '';
                imagePreview.classList.add('d-none');
                return;
            }

            // Display preview
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                imagePreview.classList.remove('d-none');
            };
            reader.readAsDataURL(file);
        });
    }

    // Form submission handling
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            // Check if file is selected
            if (fileInput.files.length === 0) {
                event.preventDefault();
                alert('Please select an image to analyze');
                return;
            }

            // Show loading spinner and disable submit button
            loadingSpinner.classList.remove('d-none');
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
        });
    }

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});
