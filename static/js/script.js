/**
 * SkillMatch AI - Client-side Interactive Script
 * Manages Drag and Drop resume uploading, file validation, and UI progress animations.
 */

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('resumeFileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');

    if (dropZone && fileInput) {
        // Trigger file picker on click
        dropZone.addEventListener('click', (e) => {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });

        // Drag & Drop handlers
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('dragover');
            }, false);
        });

        // Handle file drop
        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateFileDisplay(files[0]);
            }
        });

        // Handle file selection via input
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                updateFileDisplay(fileInput.files[0]);
            }
        });
    }

    function updateFileDisplay(file) {
        if (!file) return;

        const allowedExtensions = ['pdf', 'docx', 'doc'];
        const extension = file.name.split('.').pop().toLowerCase();

        if (!allowedExtensions.includes(extension)) {
            alert('Invalid file format! Please upload a PDF (.pdf) or Word (.docx) document.');
            fileInput.value = '';
            fileInfo.style.display = 'none';
            return;
        }

        fileName.textContent = file.name;
        fileSize.textContent = ` (${(file.size / 1024).toFixed(1)} KB)`;
        fileInfo.style.display = 'block';
    }

    // Submit form spinner handler
    if (uploadForm && submitBtn) {
        uploadForm.addEventListener('submit', () => {
            if (fileInput && fileInput.files.length > 0) {
                btnText.textContent = 'Processing & Extracting NLP Features...';
                if (btnSpinner) btnSpinner.style.display = 'inline-block';
                submitBtn.disabled = true;
            }
        });
    }

    // Animate progress bars on load
    const progressBars = document.querySelectorAll('.progress-bar-fill');
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 150);
    });
});
