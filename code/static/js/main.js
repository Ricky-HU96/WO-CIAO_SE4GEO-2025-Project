document.addEventListener('DOMContentLoaded', () => {
    const configForm = document.getElementById('config-form');
    const testBtn = document.getElementById('test-conn-btn');
    const runPipelineBtn = document.getElementById('run-pipeline-btn');
    const dashboardLink = document.getElementById('dashboard-link');

    const configStatus = document.getElementById('config-status');
    const pipelineStatus = document.getElementById('pipeline-status');

    // Helper function to display status messages
    function showStatus(element, message, type) {
        element.textContent = message;
        element.className = `status-message ${type} visible`;
        // Hide the message after 5 seconds
        setTimeout(() => {
            element.classList.remove('visible');
        }, 5000);
    }

    // Handle Config Form Submission (Set & Save)
    configForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        showStatus(configStatus, 'Saving configuration...', 'info');
        
        const configData = {
            dbName: document.getElementById('dbName').value,
            user: document.getElementById('user').value,
            password: document.getElementById('password').value,
            host: document.getElementById('host').value,
            port: document.getElementById('port').value,
        };

        try {
            const response = await fetch('/set-config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configData)
            });

            const result = await response.json();
            if (response.ok) {
                showStatus(configStatus, result.message, 'success');
                runPipelineBtn.disabled = false;
            } else {
                showStatus(configStatus, result.message, 'error');
            }
        } catch (error) {
            showStatus(configStatus, 'Network error. Is the server running?', 'error');
        }
    });

    // Handle Test Connection Button
    testBtn.addEventListener('click', async () => {
        showStatus(configStatus, 'Testing connection...', 'info');
        const configData = {
            dbName: document.getElementById('dbName').value,
            user: document.getElementById('user').value,
            password: document.getElementById('password').value,
            host: document.getElementById('host').value,
            port: document.getElementById('port').value,
        };

        try {
            const response = await fetch('/test-connection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configData)
            });
            const result = await response.json();
            showStatus(configStatus, result.message, response.ok ? 'success' : 'error');
        } catch (error) {
            showStatus(configStatus, 'Network error. Is the server running?', 'error');
        }
    });

    // Handle Run Pipeline Button
    runPipelineBtn.addEventListener('click', async () => {
        showStatus(pipelineStatus, 'Pipeline is running... This may take a few minutes. Check the server console for progress.', 'info');
        runPipelineBtn.disabled = true;

        try {
            const response = await fetch('/run-pipeline', { method: 'POST' });
            const result = await response.json();

            if (response.ok) {
                showStatus(pipelineStatus, result.message, 'success');
                dashboardLink.classList.remove('disabled');
            } else {
                showStatus(pipelineStatus, result.message, 'error');
                runPipelineBtn.disabled = false; // Re-enable on failure
            }
        } catch (error) {
            showStatus(pipelineStatus, 'Network error. Is the server running?', 'error');
            runPipelineBtn.disabled = false;
        }
    });
});