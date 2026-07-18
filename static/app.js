// Define backend URL (Update with Railway URL when deployed)
const API_BASE_URL = window.location.hostname === 'localhost' ? '' : 'https://ai-multi-agent-production-d15b.up.railway.app';

document.getElementById('trip-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const locationSelect = document.getElementById('location-select');
    const promptInput = document.getElementById('prompt');
    const promptText = promptInput.value.trim();
    if (!promptText) return;

    const fullPrompt = `Destination: ${locationSelect.value}. ${promptText}`;

    // Reset UI
    document.getElementById('hero-section').classList.add('hidden');
    document.getElementById('observability').classList.remove('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('agent-logs').innerHTML = '';
    document.querySelector('.loader').style.display = 'block';
    
    // Disable input while processing
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;
    submitBtn.style.opacity = '0.7';

    // Start SSE Connection
    const eventSource = new EventSource(`${API_BASE_URL}/stream-plan-trip?prompt=${encodeURIComponent(fullPrompt)}`);

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
            if (window.latestItinerary) {
                renderItinerary(window.latestItinerary);
            }
            return;
        }

        let desc = nodeDescriptions[data.node] || `${data.node} Agent finished processing...`;
        let statusClass = 'done';

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
        if (eventSource.readyState === EventSource.CLOSED) {
            appendLog('System', 'Connection to server closed.', 'error');
            closeConnection(eventSource, submitBtn);
        } else {
            console.log('SSE connection error, attempting to reconnect...');
        }
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
    ul.scrollTop = ul.scrollHeight;
}

function renderItinerary(data) {
    const resultSection = document.getElementById('result');
    document.getElementById('observability').classList.add('hidden'); // Hide logs when done
    resultSection.classList.remove('hidden');

    const totalDays = data.daily_plan ? data.daily_plan.length : 0;
    
    // Pull the destination from the dropdown, fallback to Dubai
    const locationSelect = document.getElementById('location-select');
    const selectedDest = locationSelect ? locationSelect.value : 'Dubai';
    const dest = data.destination || selectedDest;
    
    const costUsd = data.total_estimated_cost || 0;
    const costAed = Math.round(costUsd * 3.67);

    let html = `
        <div class="flex flex-col md:flex-row justify-between items-end md:items-center gap-6 mb-12">
            <div>
                <p class="text-secondary font-label-md uppercase tracking-wider mb-2">${totalDays} Days • ${dest}</p>
                <h2 class="font-headline-xl text-headline-xl text-on-surface">Experience Excellence</h2>
            </div>
            <div class="flex gap-4">
                <button class="px-8 py-3 rounded-full border border-outline/20 font-label-md text-on-surface hover:bg-surface-container-high transition-all flex items-center gap-2">
                    <span class="material-symbols-outlined text-[20px]" data-icon="share">share</span>
                    Share
                </button>
                <button class="px-8 py-3 rounded-full bg-secondary text-on-secondary font-label-md hover:brightness-110 transition-all shadow-lg shadow-secondary/20 flex items-center gap-2">
                    <span class="material-symbols-outlined text-[20px]" data-icon="shopping_cart">shopping_cart</span>
                    Book All (AED ${costAed})
                </button>
            </div>
        </div>
        <div class="space-y-section-gap">
    `;

    // Fallback images based on original design
    const stayImages = [
        "https://lh3.googleusercontent.com/aida-public/AB6AXuCMJuBxiIj8C-EOePKXvklRPFhb-8JTxPjm1VBTHo7eUFs1OvE79PcFesTiwI9TdM9G2wY3F1v2LrKqUSTdyXEu93xLEqmE6B9fPRFmmNEnP1J9nqLai1XSFUpetFEcmRXfzXAc229y-C93hNULGV7TKUOBkJEcZZw9EgWHuqVtdmCTzGqhFMdRdYiBNz07gXg2erVX1WPfwvPr5Kx_N_yyaLxBYUIj960NEuMoHfzZO2yGwqpGw7wJRQ",
        "https://lh3.googleusercontent.com/aida-public/AB6AXuD5StQbAQTsMFlJ49veti_NeoATmytemaI-oS3zxt4Xnz9ZLS1Ae07j31zMHshYH-rE-cBojtpW-nFeITC_jvi0CA6fudKar3-kuMKn19PeJ_tXOEJit4KuL6R6DHVKiiCnl5_hqxrhisj7N-uCTVMKlVvXa90703FS5JWwLA96Ibkt9HR9FX6ncz6rdas1P3PcKifE0AHNb4ZcDFM-OgVnhr9Q677wd6acSU-s0Pta200GcXHzCSJEmA"
    ];
    
    const activityImages = [
        "https://lh3.googleusercontent.com/aida-public/AB6AXuCOyEdnFP8c4CxkAL1lFiiM7TCPoKaMzWDiWZm0WrlA8AvgjgWkFVI11Uye2Bz4K9AyaapxXKC0OcE4MGC5_pWV0OfRiJXseWCaHXylLft4xpfjpUTMy4E0U6CTAC7M35x-hY_5-h4vNHFWQyhM5mROb92NMj7kdSwF_jONuDdv8UN5qC72igBu1J4bHocwXokDEd9aNPcVU-HIJbnE2L7S8n_xx6ed6xJuwBmhDWTR3hInAPLghKZoNQ",
        "https://lh3.googleusercontent.com/aida-public/AB6AXuCZ0H_h8f6MCT50Izq4Vvn0lgHyYVnHkrf4p8KCIfO3MAAcyzrsl3D6_zBWoVxOlhqhMyZHbITuOrX42a2UNcTyiOVp5GGx1e2fXe5qIKCyY9j01D72Cn96wLpUHwlGzGxmjkJSIAqw44C56bjkJnQNdPk7qQLYNHFhz25UGPTkC1ASK4YiUmwwIw0g0bnwBwVPIb04pDVvuVs3moMsKJ6FwyiEiq9h8vet4eOy8y8cSDe-fJpciqfnQA",
        "https://lh3.googleusercontent.com/aida-public/AB6AXuBwjx7veFbcu5d9i3TrQq8w4jKmVx7wlqFeJLVqDq8mJQtKBI3a6OUuie2L2UitnM6DjW22u6Uuqtij8wp5QjLr_6GQtTrzFd4hqwEDYhKBfs54s0UB91Le3UXJZlZ6Mi3YHcPRMYNeUG5P-s6RUayLrhxVr5euRAmZiLCRcHjO43u_QEnf5i6JbUoNcWc6hPyB6iluFlH1SS_RX5HIjYVu32cYy8Bgxt9NZxrCwYuSGZ3oHG-Ib-hIew",
        "https://lh3.googleusercontent.com/aida-public/AB6AXuAYXYHfAbN8N50vAtEmAFkGdvoZcatIDv_zj87wqzTCHkt9VhemR7hH_Lg3dDGq-CshvDiSNWUrCDARrulPdv8IPP4k8HqKPXt9OlcIJSVaU2F7iGdRZrFj_n4ENRJ6HSAsK2_PmEKiInLs9n4QMMDdPGGGKCHhefZQBQ4OhZHAGQVsuXIrWR6ZkNIm8OpNfu3dOvkLcqKjRzwNgMeCyIuTk0RmWYZw5xgPD9QQqHXX1Ae69NUGf0xorA"
    ];

    const diningImages = [
        "https://lh3.googleusercontent.com/aida-public/AB6AXuDFXW_lQZlJ9_2B9nQw6Q3K4C5jWfG8p0_X6bV2-l-p8_J9B7M1M3P5h4h2-z0w7y9l6b2_3v1Q8G2M7P5-s0-y4-b9n0_X6Q3K4C5jWfG8p0_X6bV2-l-p8_J9B7M1M3P5h4h2-z0w7y9l6b2_3v1Q8G2M7P5-s0-y4-b9n0", // Need valid placeholder, let's use a nice food one or fallback
        "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&q=80&w=1000",
        "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&q=80&w=1000",
        "https://images.unsplash.com/photo-1544148103-0773bf10d330?auto=format&fit=crop&q=80&w=1000"
    ];

    if (data.daily_plan && data.daily_plan.length > 0) {
        data.daily_plan.forEach((plan, index) => {
            const stayImg = stayImages[index % stayImages.length];
            const actImg = activityImages[index % activityImages.length];
            const dineImg = diningImages[(index + 1) % (diningImages.length - 1) + 1]; // Offset index for variety using Unsplash images
            const dayStr = String(plan.day).padStart(2, '0');
            
            html += `
                <section class="animate-in fade-in slide-in-from-bottom-4 duration-700" style="animation-delay: ${index * 150}ms">
                    <div class="flex items-center gap-4 mb-8">
                        <span class="font-headline-lg text-secondary">${dayStr}</span>
                        <h3 class="font-headline-lg text-on-surface">${plan.theme || 'Activities'}</h3>
                        <div class="h-px flex-1 bg-white/5 ml-4"></div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-gutter">
                        <!-- Stay Card -->
                        <div class="glass-card rounded-xl overflow-hidden flex flex-col">
                            <div class="h-48 overflow-hidden relative">
                                <img class="w-full h-full object-cover" src="${stayImg}" />
                                <div class="absolute top-4 left-4 bg-secondary/90 text-on-secondary px-3 py-1 rounded-full text-label-sm uppercase tracking-tighter">Stay</div>
                            </div>
                            <div class="p-6 flex-1 flex flex-col">
                                <h4 class="text-secondary font-label-md uppercase mb-2">${data.accommodation?.neighborhood || 'Luxury Suite'}</h4>
                                <p class="text-on-surface-variant text-body-md mb-4">Your base for the day</p>
                                <div class="mt-auto flex items-center justify-between text-label-sm">
                                    <span class="text-primary/60">Day ${plan.day} of ${totalDays}</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Activity Card -->
                        <div class="glass-card rounded-xl overflow-hidden flex flex-col">
                            <div class="h-48 overflow-hidden relative">
                                <img class="w-full h-full object-cover" src="${actImg}" />
                                <div class="absolute top-4 left-4 bg-primary-fixed-dim/90 text-on-primary-fixed px-3 py-1 rounded-full text-label-sm uppercase tracking-tighter">Activity</div>
                            </div>
                            <div class="p-6 flex-1 flex flex-col">
                                <h4 class="text-secondary font-label-md uppercase mb-2">Morning & Afternoon</h4>
                                <p class="text-on-surface-variant text-body-md mb-4">${plan.morning_activity}<br><br>${plan.afternoon_activity}</p>
                            </div>
                        </div>
                        
                        <!-- Dining Card -->
                        <div class="glass-card rounded-xl overflow-hidden flex flex-col">
                            <div class="h-48 overflow-hidden relative">
                                <img class="w-full h-full object-cover" src="${dineImg}" />
                                <div class="absolute top-4 left-4 bg-tertiary-fixed-dim/90 text-on-tertiary-fixed px-3 py-1 rounded-full text-label-sm uppercase tracking-tighter">Dining</div>
                            </div>
                            <div class="p-6 flex-1 flex flex-col">
                                <h4 class="text-secondary font-label-md uppercase mb-2">Evening</h4>
                                <p class="text-on-surface-variant text-body-md mb-4">${plan.evening_activity}</p>
                                ${plan.transit_notes ? `<div class="mt-4 pt-4 border-t border-white/5 text-label-sm text-primary/60">Transit: ${plan.transit_notes}</div>` : ''}
                            </div>
                        </div>
                    </div>
                </section>
            `;
        });
    }

    html += `</div>`; // Close space-y-section-gap
    
    // Add FAB Voice Hub at the bottom of results to allow user to start over
    html += `
        <div class="fixed bottom-24 left-1/2 -translate-x-1/2 z-40 group animate-in fade-in duration-700 delay-500">
            <div class="absolute inset-0 bg-secondary/20 blur-2xl rounded-full scale-150 animate-pulse"></div>
            <button onclick="document.getElementById('hero-section').classList.remove('hidden'); document.getElementById('result').classList.add('hidden'); window.scrollTo({top:0, behavior:'smooth'});" class="relative w-16 h-16 rounded-full bg-secondary text-on-secondary shadow-2xl flex items-center justify-center hover:scale-105 active:scale-95 transition-all duration-300">
                <span class="material-symbols-outlined text-[32px]" data-icon="mic" data-weight="fill">mic</span>
            </button>
            <div class="absolute bottom-full mb-4 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                <div class="glass-card px-4 py-2 rounded-full text-label-sm text-primary">
                    "Modify my itinerary"
                </div>
            </div>
        </div>
    `;

    resultSection.innerHTML = html;
    
    // Re-initialize micro-interactions for new cards
    document.querySelectorAll('.glass-card').forEach(card => {
        card.addEventListener('mouseenter', () => {});
    });

    // Scroll to results
    setTimeout(() => {
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }, 100);
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
            let options = {};
            if (MediaRecorder.isTypeSupported('audio/webm')) {
                options = { mimeType: 'audio/webm' };
            } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
                options = { mimeType: 'audio/mp4' };
            }
            mediaRecorder = new MediaRecorder(stream, options);
            
            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const mimeType = mediaRecorder.mimeType || options.mimeType || 'audio/mp4';
                const fileExt = mimeType.includes('webm') ? 'webm' : 'mp4';
                const audioBlob = new Blob(audioChunks, { type: mimeType });
                audioChunks = [];
                
                // Show loading state on mic button
                micBtn.classList.remove('mic-recording');
                micBtn.classList.add('opacity-50');
                micBtn.title = "Transcribing...";
                
                // Send to backend
                const formData = new FormData();
                formData.append('audio', audioBlob, `recording.${fileExt}`);
                
                try {
                    const response = await fetch(`${API_BASE_URL}/transcribe`, {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        const promptInput = document.getElementById('prompt');
                        // append to existing text
                        promptInput.value = (promptInput.value + " " + data.text).trim();
                    } else {
                        const errorData = await response.json().catch(() => ({}));
                        console.error('Transcription failed:', errorData);
                        alert(`Transcription failed: ${errorData.detail || 'Server error.'}`);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error connecting to transcription service.');
                }
                
                micBtn.classList.remove('opacity-50');
                micBtn.title = "Click to start/stop recording";
                // Stop all audio tracks
                stream.getTracks().forEach(track => track.stop());
            };

            audioChunks = [];
            mediaRecorder.start();
            isRecording = true;
            micBtn.classList.add('mic-recording');
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
