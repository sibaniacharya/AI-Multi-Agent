document.getElementById('trip-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const promptInput = document.getElementById('prompt');
    const promptText = promptInput.value.trim();
    if (!promptText) return;

    // Reset UI
    document.getElementById('observability').classList.remove('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('agent-logs').innerHTML = '';
    document.querySelector('.loader').style.display = 'block';
    
    // Disable input while processing
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;
    submitBtn.style.opacity = '0.7';

    // Start SSE Connection
    const eventSource = new EventSource(`/stream-plan-trip?prompt=${encodeURIComponent(promptText)}`);

    const nodeDescriptions = {
        'orchestrator': 'Orchestrator is extracting constraints and preferences...',
        'destination': 'Destination Agent is researching attractions...',
        'logistics': 'Logistics Agent is planning routes and accommodations...',
        'budget': 'Budget Agent is estimating costs...',
        'synthesize': 'Synthesizing data into a cohesive itinerary...',
        'review': 'Review Agent is QA-ing against constraints...'
    };

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.error) {
            appendLog('System', `Error: ${data.error}`, 'error');
            closeConnection(eventSource, submitBtn);
            return;
        }

        if (data.node === 'DONE') {
            closeConnection(eventSource, submitBtn);
            document.querySelector('.loader').style.display = 'none';
            // Render the latest itinerary even if the review failed max retries
            if (window.latestItinerary) {
                renderItinerary(window.latestItinerary);
            }
            return;
        }

        let desc = nodeDescriptions[data.node] || `${data.node} Agent finished processing...`;
        let statusClass = 'done';

        // Check if there's a review failure or success
        if (data.node === 'review' && data.qa_review) {
            if (!data.qa_review.is_valid) {
                desc = `Review Failed! Feedback: ${data.qa_review.feedback} (Retrying... Attempt ${data.retry_count})`;
                statusClass = 'review-fail';
            } else {
                desc = `Review Passed! Feedback: ${data.qa_review.feedback}`;
                statusClass = 'done';
            }
        }

        appendLog(data.node, desc, statusClass);

        // If itinerary is present and it's the final output (or just when it arrives)
        // Wait, the review node might fail, so we should only render the itinerary if review passed.
        // Actually, the backend sends the itinerary at 'synthesize'. Let's store it globally.
        if (data.itinerary) {
            window.latestItinerary = data.itinerary;
        }

        if (data.node === 'review' && data.qa_review && data.qa_review.is_valid) {
            if (window.latestItinerary) {
                renderItinerary(window.latestItinerary);
            }
        }
    };

    eventSource.onerror = function(err) {
        appendLog('System', 'Connection to server lost or interrupted.', 'error');
        closeConnection(eventSource, submitBtn);
    };
});

function closeConnection(source, btn) {
    source.close();
    btn.disabled = false;
    btn.style.opacity = '1';
}

function appendLog(agentName, text, statusClass) {
    const ul = document.getElementById('agent-logs');
    const li = document.createElement('li');
    li.className = `agent-log-item ${statusClass}`;
    li.innerHTML = `
        <span class="agent-badge">${agentName}</span>
        <span class="log-text">${text}</span>
    `;
    ul.appendChild(li);
    // Smooth scroll to bottom of logs
    ul.scrollTop = ul.scrollHeight;
}

function renderItinerary(data) {
    const resultSection = document.getElementById('result');
    resultSection.classList.remove('hidden');

    let html = `
        <div class="trip-summary">
            <div class="summary-box glass">
                <h3>Destination</h3>
                <p>${data.destination || 'Dubai'}</p>
            </div>
            <div class="summary-box glass">
                <h3>Est. Cost</h3>
                <p>$${data.total_estimated_cost || 'Unknown'}</p>
            </div>
        </div>
        
        <div class="itinerary-container">
    `;

    if (data.daily_plan && data.daily_plan.length > 0) {
        data.daily_plan.forEach(plan => {
            html += `
                <div class="day-card glass">
                    <div class="day-card-header">
                        <div class="day-title">
                            <h3>Day ${plan.day}</h3>
                            <p class="day-theme">${plan.theme || 'Activities'}</p>
                        </div>
                        <div class="day-meta">
                            <span class="stay-label">Stay: ${data.accommodation?.neighborhood || 'Unknown'}</span>
                        </div>
                    </div>
                    
                    <div class="day-grid">
                        <div class="time-block">
                            <span class="time-label">MORNING</span>
                            <div class="time-content">${plan.morning_activity || 'Free time'}</div>
                        </div>
                        <div class="time-block">
                            <span class="time-label">AFTERNOON</span>
                            <div class="time-content">${plan.afternoon_activity || 'Free time'}</div>
                        </div>
                        <div class="time-block">
                            <span class="time-label">EVENING</span>
                            <div class="time-content">${plan.evening_activity || 'Free time'}</div>
                        </div>
                    </div>
            `;
            if (plan.transit_notes) {
                html += `
                    <div class="transit-meta">
                        <strong>Transit Notes:</strong> ${plan.transit_notes}
                    </div>
                `;
            }
            html += `</div>`; // Close day-card
        });
    }

    html += `</div>`; // Close itinerary-container
    resultSection.innerHTML = html;
    
    // Scroll to results
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// Speech-to-Text Logic
const micBtn = document.getElementById('mic-btn');
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

micBtn.addEventListener('click', async () => {
    if (!isRecording) {
        // Start recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = [];
                
                // Show loading state on mic button
                micBtn.classList.remove('recording');
                micBtn.style.opacity = '0.5';
                micBtn.title = "Transcribing...";
                
                // Send to backend
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.webm');
                
                try {
                    const response = await fetch('/transcribe', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        const promptInput = document.getElementById('prompt');
                        promptInput.value = data.text;
                    } else {
                        console.error('Transcription failed');
                        alert('Transcription failed. Please try again.');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error connecting to transcription service.');
                }
                
                micBtn.style.opacity = '1';
                micBtn.title = "Click to start/stop recording";
                // Stop all audio tracks
                stream.getTracks().forEach(track => track.stop());
            };

            audioChunks = [];
            mediaRecorder.start();
            isRecording = true;
            micBtn.classList.add('recording');
            micBtn.title = "Click to stop recording";
        } catch (err) {
            console.error("Error accessing microphone:", err);
            alert("Could not access the microphone. Please check permissions.");
        }
    } else {
        // Stop recording
        mediaRecorder.stop();
        isRecording = false;
    }
});
