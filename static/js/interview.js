const sessionId = localStorage.getItem('session_id');
let mediaRecorder;
let audioChunks = [];
let audioContext;
let analyser;
let microphone;
let scriptProcessor;
let isRecording = false;
let silenceStart = null;
let vadState = 'IDLE'; // IDLE, LISTENING, SPEAKING, PROCESSING
const SILENCE_THRESHOLD = 0.02; // Adjust based on testing
const SILENCE_DURATION = 2000; // 2 seconds of silence to trigger stop

// Initialize
window.addEventListener('DOMContentLoaded', () => {
    if (!sessionId) {
        alert('No active session found. Redirecting to home.');
        window.location.href = '/';
        return;
    }

    const firstQuestion = JSON.parse(localStorage.getItem('first_question'));
    displayQuestion(firstQuestion.question_text);
    // Timer will start after user clicks start
});

document.getElementById('init-btn').addEventListener('click', async () => {
    document.getElementById('start-overlay').style.display = 'none';
    await initVAD();
    startTimer();
    document.getElementById('start-overlay').style.display = 'none';
    await initVAD();
    startTimer();
});

document.getElementById('end-btn').addEventListener('click', () => {
    if (confirm('Are you sure you want to end the interview early?')) {
        endSession();
    }
});

function displayQuestion(text) {
    document.getElementById('interviewer-text').innerText = text;
    speakText(text);
}

let isAiSpeaking = false;

function speakText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        
        utterance.onstart = () => {
            isAiSpeaking = true;
            console.log('AI started speaking');
        };
        
        utterance.onend = () => {
            isAiSpeaking = false;
            console.log('AI stopped speaking');
            // Resume listening state if needed
            if (vadState === 'IDLE' || vadState === 'LISTENING') {
                vadState = 'LISTENING';
                updateVADStatus('LISTENING', 'Listening...');
            }
        };

        window.speechSynthesis.speak(utterance);
    } else {
        console.warn('TTS not supported.');
    }
}

async function initVAD() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
        
        // Show video feed
        const videoElement = document.getElementById('user-video');
        if (videoElement) {
            videoElement.srcObject = stream;
            // Initialize face detection once video metadata is loaded
            videoElement.onloadedmetadata = () => {
                videoElement.play();
                initFaceDetection();
            };
        }
        
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        microphone = audioContext.createMediaStreamSource(stream);
        scriptProcessor = audioContext.createScriptProcessor(2048, 1, 1);

        analyser.smoothingTimeConstant = 0.8;
        analyser.fftSize = 1024;

        microphone.connect(analyser);
        analyser.connect(scriptProcessor);
        scriptProcessor.connect(audioContext.destination);

        // Prepare MediaRecorder for the actual audio capture
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await submitAnswer(audioBlob);
        };

        scriptProcessor.onaudioprocess = (event) => {
            const input = event.inputBuffer.getChannelData(0);
            let sum = 0;
            for (let i = 0; i < input.length; i++) {
                sum += input[i] * input[i];
            }
            const rms = Math.sqrt(sum / input.length);
            handleVAD(rms);
        };

        updateVADStatus('LISTENING', 'Listening...');
        vadState = 'LISTENING';

    } catch (err) {
        console.error('Error initializing VAD:', err);
        alert('Microphone access is required for this interview.');
    }
}

function handleVAD(volume) {
    if (vadState === 'PROCESSING') return;
    if (isAiSpeaking) return; // Ignore input while AI is speaking

    if (volume > SILENCE_THRESHOLD) {
        // Speech detected
        if (vadState === 'LISTENING') {
            startRecording();
        }
        vadState = 'SPEAKING';
        silenceStart = null;
        updateVADStatus('SPEAKING', 'Speaking...');
    } else {
        // Silence detected
        if (vadState === 'SPEAKING') {
            if (!silenceStart) {
                silenceStart = Date.now();
            } else if (Date.now() - silenceStart > SILENCE_DURATION) {
                // Silence timeout reached
                stopRecording();
            }
        }
    }
}

function startRecording() {
    console.log('Starting recording...');
    audioChunks = [];
    mediaRecorder.start();
    vadState = 'SPEAKING';
    updateVADStatus('SPEAKING', 'Recording...');
}

function stopRecording() {
    console.log('Stopping recording...');
    mediaRecorder.stop();
    vadState = 'PROCESSING';
    updateVADStatus('PROCESSING', 'Processing answer...');
}

function updateVADStatus(state, text) {
    const icon = document.getElementById('vad-icon');
    const textElem = document.getElementById('vad-text');
    
    textElem.innerText = text;
    
    if (state === 'LISTENING') {
        icon.innerText = '👂';
        document.getElementById('vad-status').className = 'status-indicator listening';
    } else if (state === 'SPEAKING') {
        icon.innerText = '🎤';
        document.getElementById('vad-status').className = 'status-indicator recording';
    } else if (state === 'PROCESSING') {
        icon.innerText = '⏳';
        document.getElementById('vad-status').className = 'status-indicator processing';
    }
}

async function submitAnswer(audioBlob) {
    const formData = new FormData();
    formData.append('file', audioBlob, 'answer.wav');

    try {
        const response = await fetch(`/api/v1/session/${sessionId}/audio`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.next_question) {
            displayQuestion(result.next_question.question_text);
            // Feedback is intentionally hidden now
            
            // Resume listening
            vadState = 'LISTENING';
            updateVADStatus('LISTENING', 'Listening...');
        } else {
            endSession();
        }

    } catch (error) {
        console.error('Error submitting answer:', error);
        alert('Error submitting answer. Please refresh.');
    }
}

function startTimer() {
    let seconds = 600; // Default 10 mins
    const display = document.getElementById('time-display');
    
    const interval = setInterval(() => {
        seconds--;
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        display.innerText = `${mins}:${secs.toString().padStart(2, '0')}`;
        
        if (seconds <= 0) {
            clearInterval(interval);
            endSession();
        }
    }, 1000);
}

async function endSession() {
    // Stop any ongoing recording
    if (isRecording) {
        mediaRecorder.stop();
        isRecording = false;
    }
    
    // Stop VAD
    if (audioContext) {
        audioContext.close();
    }

    const statusDiv = document.getElementById('interviewer-text');
    statusDiv.innerText = "Generating your interview report... please wait.";
    speakText("Thank you for your time. I am generating your feedback report now.");

    // Calculate final missing time if currently missing
    if (isFaceMissing && missingStartTime) {
        faceMissingDuration += (Date.now() - missingStartTime) / 1000;
    }

    try {
        // Send stats first
        await fetch(`/api/v1/session/${sessionId}/end`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ face_missing_seconds: Math.round(faceMissingDuration) })
        });

        const response = await fetch(`/api/v1/session/${sessionId}/final`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Interview_Report_${sessionId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            
            statusDiv.innerText = "Report downloaded! Redirecting to home in 5 seconds...";
            setTimeout(() => {
                window.location.href = '/';
            }, 5000);
        } else {
            alert('Failed to generate report.');
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Error fetching report:', error);
        alert('Error generating report.');
        window.location.href = '/';
    }
}

// Face Detection Logic
let faceModel = null;
let lastFaceDetectedTime = Date.now();
let faceMissingDuration = 0; // Total seconds face was missing
let isFaceMissing = false;
let missingStartTime = null;

const FACE_CHECK_INTERVAL = 500; // Check every 0.5 second for better accuracy
const NO_FACE_THRESHOLD = 5000; // Alert after 5 seconds of no face

async function initFaceDetection() {
    const statusElem = document.getElementById('face-status');
    if (statusElem) {
        statusElem.style.display = 'block';
        statusElem.innerText = 'Loading AI...';
    }

    try {
        console.log('Loading face detection model...');
        faceModel = await blazeface.load();
        console.log('Face detection model loaded.');
        
        if (statusElem) statusElem.innerText = 'Active';
        
        // Start detection loop
        detectFaceLoop();
    } catch (err) {
        console.error('Error loading face model:', err);
        if (statusElem) statusElem.innerText = 'Error';
    }
}

async function detectFaceLoop() {
    const video = document.getElementById('user-video');
    const statusElem = document.getElementById('face-status');
    
    if (faceModel && video && video.readyState === 4) {
        try {
            const returnTensors = false;
            const predictions = await faceModel.estimateFaces(video, returnTensors);
            
            if (predictions.length > 0) {
                // Face found
                lastFaceDetectedTime = Date.now();
                hideFaceAlert();
                
                if (statusElem) {
                    statusElem.innerText = 'Face Detected';
                    statusElem.style.color = '#4ade80'; // Green
                }

                if (isFaceMissing) {
                    // Just returned
                    if (missingStartTime) {
                        const missingSeconds = (Date.now() - missingStartTime) / 1000;
                        faceMissingDuration += missingSeconds;
                        console.log(`Face returned. Missing for ${missingSeconds.toFixed(1)}s. Total: ${faceMissingDuration.toFixed(1)}s`);
                        missingStartTime = null;
                    }
                    isFaceMissing = false;
                }
            } else {
                // No face found
                if (statusElem) {
                    statusElem.innerText = 'No Face';
                    statusElem.style.color = '#f87171'; // Red
                }

                if (!isFaceMissing) {
                    isFaceMissing = true;
                    missingStartTime = Date.now();
                    console.log('Face lost...');
                }
                checkFaceAlert();
            }
        } catch (err) {
            console.warn('Face detection error:', err);
        }
    }
    
    // Schedule next check
    if (sessionId) { // Only continue if session is active
        setTimeout(detectFaceLoop, FACE_CHECK_INTERVAL);
    }
}

function checkFaceAlert() {
    const timeSinceLastFace = Date.now() - lastFaceDetectedTime;
    
    if (timeSinceLastFace > NO_FACE_THRESHOLD) {
        showFaceAlert();
        playBeep();
    }
}

function showFaceAlert() {
    const container = document.querySelector('.user-video-container');
    if (container) {
        container.style.borderColor = 'red';
        container.style.boxShadow = '0 0 15px red';
    }
}

function hideFaceAlert() {
    const container = document.querySelector('.user-video-container');
    if (container) {
        container.style.borderColor = '#e5e7eb';
        container.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    }
}

function playBeep() {
    // Simple beep using AudioContext
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, ctx.currentTime); // A5
        gain.gain.setValueAtTime(0.1, ctx.currentTime);
        
        osc.start();
        osc.stop(ctx.currentTime + 0.2); // Short beep
    } catch (e) {
        console.error('AudioContext beep error:', e);
    }
}
