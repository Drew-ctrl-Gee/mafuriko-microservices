let currentLanguage = 'en';
let recognition = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadWeather();
    setInterval(loadWeather, 300000); // Refresh every 5 min
    initVoiceRecognition();
});

// Load weather
async function loadWeather() {
    try {
        const response = await fetch('/api/weather');
        const data = await response.json();
        
        const badge = document.getElementById('weatherBadge');
        badge.innerHTML = `<i class="fas fa-thermometer-half"></i> ${data.city}: ${data.temperature_c}°C, ${data.weather_description}`;
    } catch (error) {
        console.error('Weather error:', error);
    }
}

// Set language
function setLanguage(lang) {
    currentLanguage = lang;
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });
}

// Send message
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    if (!message) return;
    
    addMessage(message, 'user');
    input.value = '';
    
    // Show typing indicator
    const typingId = showTyping();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message, language: currentLanguage})
        });
        
        const data = await response.json();
        removeTyping(typingId);
        addBotMessage(data);
    } catch (error) {
        removeTyping(typingId);
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    }
}

function sendQuickMessage(msg) {
    document.getElementById('messageInput').value = msg;
    sendMessage();
}

function addMessage(text, sender) {
    const messages = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;
    msgDiv.innerHTML = `
        <div class="message-avatar">${sender === 'user' ? '👤' : '🤖'}</div>
        <div class="message-content">${text}</div>
    `;
    messages.appendChild(msgDiv);
    messages.scrollTop = messages.scrollHeight;
}

function addBotMessage(data) {
    const messages = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message bot-message';
    
    let content = `<p>${data.text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')}</p>`;
    
    if (data.weather) {
        content += `
            <div style="margin-top:15px; padding:15px; background:rgba(79,172,254,0.15); border-radius:10px;">
                <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:10px;">
                    <div>🌡️ ${data.weather.temperature_c}°C</div>
                    <div>💧 ${data.weather.humidity_percent}%</div>
                    <div>🌧️ ${data.weather.rainfall_mm}mm</div>
                    <div>💨 ${data.weather.wind_speed_ms} m/s</div>
                </div>
            </div>
        `;
    }
    
    if (data.alternatives && data.alternatives.length) {
        content += `<div style="margin-top:15px; padding:15px; background:rgba(0,242,254,0.1); border-radius:10px;">
            <strong>🛡️ Safer Alternative Routes:</strong>
            <ul style="margin-top:10px;">
                ${data.alternatives.map(alt => `<li>• ${alt}</li>`).join('')}
            </ul>
        </div>`;
    }
    
    if (data.safety_message) {
        content += `<div style="margin-top:10px; padding:10px; border-left:4px solid ${
            data.risk_level === 'high' ? '#e74c3c' : 
            data.risk_level === 'medium' ? '#f39c12' : '#27ae60'
        }; background:rgba(255,255,255,0.05);">
            ${data.safety_message}
        </div>`;
    }
    
    msgDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">${content}</div>
    `;
    messages.appendChild(msgDiv);
    messages.scrollTop = messages.scrollHeight;
}

function showTyping() {
    const messages = document.getElementById('chatMessages');
    const id = 'typing-' + Date.now();
    messages.innerHTML += `
        <div class="message bot-message" id="${id}">
            <div class="message-avatar">🤖</div>
            <div class="message-content">💭 Typing...</div>
        </div>
    `;
    messages.scrollTop = messages.scrollHeight;
    return id;
}

function removeTyping(id) {
    document.getElementById(id)?.remove();
}

// Voice Recognition
function initVoiceRecognition() {
    if (!('webkitSpeechRecognition' in window)) return;
    
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = currentLanguage === 'sw' ? 'sw-KE' : 'en-KE';
    
    recognition.onresult = (event) => {
        document.getElementById('messageInput').value = event.results[0][0].transcript;
        sendMessage();
    };
    
    recognition.onend = () => {
        document.querySelector('.voice-btn').classList.remove('recording');
    };
}

function toggleVoiceInput() {
    if (!recognition) {
        alert('Voice input not supported in your browser');
        return;
    }
    
    const btn = document.querySelector('.voice-btn');
    if (btn.classList.contains('recording')) {
        recognition.stop();
    } else {
        recognition.lang = currentLanguage === 'sw' ? 'sw-KE' : 'en-KE';
        recognition.start();
        btn.classList.add('recording');
    }
}