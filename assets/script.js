/**
 * ==============================================================================
 * Resume Mining and Classification System - Client JavaScript
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const dropZone = document.getElementById('drop-zone');
    const pdfFileInput = document.getElementById('pdf-file-input');
    const browseBtn = document.getElementById('browse-btn');
    const filePreviewStrip = document.getElementById('file-preview-strip');
    const selectedFileName = document.getElementById('selected-file-name');
    const selectedFileSize = document.getElementById('selected-file-size');
    const clearFileBtn = document.getElementById('clear-file-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const alertBox = document.getElementById('alert-box');
    const alertMsgText = document.getElementById('alert-msg-text');

    // Sections
    const uploadCard = document.getElementById('upload-card');
    const loadingCard = document.getElementById('loading-card');
    const resultsContainer = document.getElementById('results-container');
    const analyzeAnotherBtn = document.getElementById('analyze-another-btn');

    // Loading Tracker Steps
    const pSteps = [
        document.getElementById('p-step-1'),
        document.getElementById('p-step-2'),
        document.getElementById('p-step-3'),
        document.getElementById('p-step-4')
    ];

    // Results Display Elements
    const resFileName = document.getElementById('res-file-name');
    const predCategoryName = document.getElementById('pred-category-name');
    const predConfidenceVal = document.getElementById('pred-confidence-val');
    const confidenceBadgeWrap = document.getElementById('confidence-badge-wrap');
    const predStatusTag = document.getElementById('pred-status-tag');
    const predExplanationMsg = document.getElementById('pred-explanation-msg');

    const skillsTotalCount = document.getElementById('skills-total-count');
    const skillsTagWrap = document.getElementById('skills-tag-wrap');

    const infoEmailVal = document.getElementById('info-email-val');
    const infoPhoneVal = document.getElementById('info-phone-val');
    const infoLinksVal = document.getElementById('info-links-val');
    const infoDocMetrics = document.getElementById('info-doc-metrics');
    const infoSummaryText = document.getElementById('info-summary-text');

    const toggleRawText = document.getElementById('toggle-raw-text');
    const rawTextBody = document.getElementById('raw-text-body');
    const textChevron = document.getElementById('text-chevron');
    const rawTextPre = document.getElementById('raw-text-pre');

    // Currently selected File
    let selectedFile = null;

    // ==========================================================================
    // 1. File Upload & Drag-and-Drop
    // ==========================================================================

    browseBtn.addEventListener('click', () => {
        pdfFileInput.click();
    });

    dropZone.addEventListener('click', (e) => {
        if (e.target !== browseBtn) {
            pdfFileInput.click();
        }
    });

    // Drag-over styling
    ['dragenter', 'dragover'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            processSelectedFile(files[0]);
        }
    });

    pdfFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            processSelectedFile(e.target.files[0]);
        }
    });

    clearFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUploadState();
    });

    function processSelectedFile(file) {
        hideAlert();

        // Validate format
        if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
            showAlert('Please select a valid PDF file (.pdf).');
            return;
        }

        // Validate size (16 MB)
        if (file.size > 16 * 1024 * 1024) {
            showAlert('File is too large. Maximum supported PDF size is 16 MB.');
            return;
        }

        selectedFile = file;
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatBytes(file.size);

        dropZone.classList.add('hidden');
        filePreviewStrip.classList.remove('hidden');
        analyzeBtn.disabled = false;
    }

    function resetUploadState() {
        selectedFile = null;
        pdfFileInput.value = '';
        dropZone.classList.remove('hidden');
        filePreviewStrip.classList.add('hidden');
        analyzeBtn.disabled = true;
        hideAlert();
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    function showAlert(msg) {
        alertMsgText.textContent = msg;
        alertBox.classList.remove('hidden');
    }

    function hideAlert() {
        alertBox.classList.add('hidden');
    }

    // ==========================================================================
    // 2. Submit & Analyze Resume
    // ==========================================================================

    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        hideAlert();
        startLoadingAnimation();

        const formData = new FormData();
        formData.append('resume_pdf', selectedFile);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Server failed to analyze the resume.');
            }

            renderPredictionResults(data);

        } catch (err) {
            stopLoadingAnimation();
            showAlert(err.message || 'Error occurred while analyzing resume.');
        }
    });

    analyzeAnotherBtn.addEventListener('click', () => {
        resultsContainer.classList.add('hidden');
        uploadCard.classList.remove('hidden');
        resetUploadState();
        uploadCard.scrollIntoView({ behavior: 'smooth' });
    });

    // ==========================================================================
    // 3. Loading Animation
    // ==========================================================================

    let trackerTimers = [];

    function startLoadingAnimation() {
        uploadCard.classList.add('hidden');
        resultsContainer.classList.add('hidden');
        loadingCard.classList.remove('hidden');

        pSteps.forEach(s => {
            s.className = 'track-step';
        });
        pSteps[0].classList.add('active');

        // Progressive visual steps
        trackerTimers.push(setTimeout(() => {
            pSteps[0].classList.replace('active', 'done');
            pSteps[1].classList.add('active');
        }, 500));

        trackerTimers.push(setTimeout(() => {
            pSteps[1].classList.replace('active', 'done');
            pSteps[2].classList.add('active');
        }, 1100));

        trackerTimers.push(setTimeout(() => {
            pSteps[2].classList.replace('active', 'done');
            pSteps[3].classList.add('active');
        }, 1700));
    }

    function stopLoadingAnimation() {
        trackerTimers.forEach(t => clearTimeout(t));
        trackerTimers = [];
        loadingCard.classList.add('hidden');
        uploadCard.classList.remove('hidden');
    }

    // ==========================================================================
    // 4. Render Results
    // ==========================================================================

    function renderPredictionResults(data) {
        // Complete last step
        pSteps[3].classList.replace('active', 'done');

        setTimeout(() => {
            loadingCard.classList.add('hidden');
            resultsContainer.classList.remove('hidden');

            // 1. Meta & Category
            resFileName.textContent = data.filename || 'resume.pdf';
            const pred = data.prediction || {};
            predCategoryName.textContent = pred.category || 'General';

            // Confidence Score
            if (pred.confidence !== null && pred.confidence !== undefined) {
                confidenceBadgeWrap.classList.remove('hidden');
                predConfidenceVal.textContent = pred.confidence + '%';
            } else {
                confidenceBadgeWrap.classList.add('hidden');
            }

            // Model Status
            if (pred.is_model_trained) {
                predStatusTag.className = 'model-status-tag';
                predStatusTag.innerHTML = `<i class="fa-solid fa-circle-check"></i> ML Model Active`;
            } else {
                predStatusTag.className = 'model-status-tag placeholder';
                predStatusTag.innerHTML = `<i class="fa-solid fa-clock-rotate-left"></i> Standby Baseline`;
            }

            predExplanationMsg.textContent = pred.message || 'Resume classified.';

            // 2. Extracted Skills
            const skills = data.extracted_skills || [];
            skillsTotalCount.textContent = `${skills.length} Detected`;
            if (skills.length > 0) {
                skillsTagWrap.innerHTML = skills
                    .map(s => `<span class="skill-pill"><i class="fa-solid fa-check"></i> ${escapeHtml(s)}</span>`)
                    .join('');
            } else {
                skillsTagWrap.innerHTML = `<span class="text-muted">No matching skills detected from taxonomy.</span>`;
            }

            // 3. Important Information
            const info = data.candidate_info || {};

            // Emails
            infoEmailVal.innerHTML = (info.emails && info.emails.length > 0)
                ? info.emails.map(e => `<a href="mailto:${escapeHtml(e)}">${escapeHtml(e)}</a>`).join(', ')
                : `<span class="text-muted">None found</span>`;

            // Phones
            infoPhoneVal.innerHTML = (info.phones && info.phones.length > 0)
                ? info.phones.map(p => `<a href="tel:${escapeHtml(p)}">${escapeHtml(p)}</a>`).join(', ')
                : `<span class="text-muted">None found</span>`;

            // Links
            if (info.links && info.links.length > 0) {
                infoLinksVal.innerHTML = info.links
                    .map(l => {
                        const href = l.startsWith('http') ? l : 'https://' + l;
                        return `<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer"><i class="fa-solid fa-arrow-up-right-from-square"></i> ${escapeHtml(l)}</a>`;
                    }).join('');
            } else {
                infoLinksVal.innerHTML = `<span class="text-muted">None found</span>`;
            }

            // Metrics
            infoDocMetrics.textContent = `${data.page_count || 1} Page(s) • ${data.word_count || 0} Words`;

            // Summary
            infoSummaryText.textContent = info.summary || 'Summary unavailable.';

            // 4. Raw Text
            rawTextPre.textContent = data.raw_text_preview || 'No text extracted.';

            // Scroll to results
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
        }, 400);
    }

    // Toggle Raw Text Box
    toggleRawText.addEventListener('click', () => {
        const isHidden = rawTextBody.classList.contains('hidden');
        if (isHidden) {
            rawTextBody.classList.remove('hidden');
            textChevron.classList.add('rotated');
        } else {
            rawTextBody.classList.add('hidden');
            textChevron.classList.remove('rotated');
        }
    });

    // ==========================================================================
    // 5. Data Mining Dashboard - Load Training Metrics
    // ==========================================================================

    async function loadDashboardMetrics() {
        try {
            const res = await fetch('/metrics');
            const data = await res.json();

            if (data.available && data.metrics) {
                const m = data.metrics;
                document.getElementById('not-trained-banner').classList.add('hidden');

                if (m.total_resumes) document.getElementById('d-total-resumes').textContent = m.total_resumes.toLocaleString();
                if (m.num_categories) document.getElementById('d-categories').textContent = m.num_categories;
                if (m.train_accuracy) document.getElementById('d-train-acc').textContent = m.train_accuracy + '%';
                if (m.test_accuracy) document.getElementById('d-test-acc').textContent = m.test_accuracy + '%';
                if (m.precision) document.getElementById('d-precision').textContent = m.precision + '%';
                if (m.recall) document.getElementById('d-recall').textContent = m.recall + '%';
                if (m.f1_score) document.getElementById('d-f1').textContent = m.f1_score + '%';
                if (m.best_model) document.getElementById('d-model-name').textContent = m.best_model;

                if (m.has_confusion_matrix_image) {
                    document.getElementById('cm-container').classList.remove('hidden');
                }
            } else {
                // Keep the "Training in Progress" banner visible
                document.getElementById('not-trained-banner').classList.remove('hidden');
            }
        } catch (e) {
            console.log('Metrics not available yet:', e);
        }
    }

    loadDashboardMetrics();

    // HTML escape utility
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
