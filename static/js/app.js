let jdData = null;
let resumeData = null;

document.getElementById('jd-upload').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/v1/upload/jd', {
            method: 'POST',
            body: formData
        });
        jdData = await response.json();
        document.getElementById('jd-status').innerText = '✅ Uploaded: ' + jdData.role_title;
        checkReady();
    } catch (error) {
        console.error('Error uploading JD:', error);
        document.getElementById('jd-status').innerText = '❌ Error uploading JD: ' + error.message;
        // Try to read response body if available
        if (error.response) {
             const errData = await error.response.json();
             document.getElementById('jd-status').innerText += ' - ' + (errData.detail || JSON.stringify(errData));
        }
    }
});

document.getElementById('resume-upload').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/v1/upload/resume', {
            method: 'POST',
            body: formData
        });
        resumeData = await response.json();
        document.getElementById('resume-status').innerText = '✅ Uploaded: ' + (resumeData.candidate_name || 'Resume');
        checkReady();
    } catch (error) {
        console.error('Error uploading Resume:', error);
        document.getElementById('resume-status').innerText = '❌ Error uploading Resume: ' + error.message;
    }
});

function checkReady() {
    if (jdData && resumeData) {
        document.getElementById('start-btn').disabled = false;
    }
}

document.getElementById('start-btn').addEventListener('click', async () => {
    const btn = document.getElementById('start-btn');
    btn.disabled = true;
    btn.innerText = 'Building Persona...';

    try {
        // 1. Build Persona
        const personaResponse = await fetch('/api/v1/agent/build', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jd: jdData, resume: resumeData })
        });
        const persona = await personaResponse.json();

        // 2. Start Session
        const duration = parseInt(document.getElementById('duration').value);
        const sessionResponse = await fetch('/api/v1/session/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent_persona: persona, duration_minutes: duration })
        });
        const session = await sessionResponse.json();

        // 3. Redirect to interview
        localStorage.setItem('session_id', session.session_id);
        localStorage.setItem('first_question', JSON.stringify(session.first_question));
        window.location.href = '/interview.html';

    } catch (error) {
        console.error('Error starting session:', error);
        btn.innerText = 'Error - Try Again';
        btn.disabled = false;
    }
});
