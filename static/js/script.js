class ChatBot {
    constructor() {
        this.socket = io();
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        
        this.initializeElements();
        this.setupEventListeners();
        this.setupSocketListeners();
    }
    
    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.voiceBtn = document.getElementById('voiceBtn');
        this.fileBtn = document.getElementById('fileBtn');
        this.fileInput = document.getElementById('fileInput');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.connectionStatus = document.getElementById('connection-status');
    }
    
    setupEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        this.messageInput.addEventListener('input', () => {
            this.socket.emit('typing', { typing: true });
        });
        
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceRecording());
        this.fileBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
    }
    
    setupSocketListeners() {
        this.socket.on('connect', () => {
            this.connectionStatus.textContent = 'Connected';
            this.connectionStatus.style.color = '#4CAF50';
        });
        
        this.socket.on('disconnect', () => {
            this.connectionStatus.textContent = 'Disconnected';
            this.connectionStatus.style.color = '#f44336';
        });
        
        this.socket.on('bot_response', (data) => {
            this.hideTypingIndicator();
            this.displayMessage(data.message, 'bot', data.sentiment);
        });
        
        this.socket.on('bot_typing', (data) => {
            if (data.typing) {
                this.showTypingIndicator();
            }
        });
        
        this.socket.on('voice_response', (data) => {
            this.playAudio(data.audio);
        });
        
        this.socket.on('error', (data) => {
            this.displayMessage(data.message, 'error');
        });
    }
    
    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        this.displayMessage(message, 'user');
        this.socket.emit('user_message', { message: message, type: 'text' });
        this.messageInput.value = '';
        this.showTypingIndicator();
    }
    
    displayMessage(message, sender, sentiment = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (sentiment) {
            contentDiv.setAttribute('data-sentiment', sentiment);
        }
        
        const messageText = document.createElement('p');
        messageText.textContent = message;
        contentDiv.appendChild(messageText);
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    async toggleVoiceRecording() {
        if (!this.isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                this.mediaRecorder = new MediaRecorder(stream);
                this.audioChunks = [];
                
                this.mediaRecorder.ondataavailable = (event) => {
                    this.audioChunks.push(event.data);
                };
                
                this.mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                    this.sendVoiceMessage(audioBlob);
                };
                
                this.mediaRecorder.start();
                this.isRecording = true;
                this.voiceBtn.classList.add('active');
                this.voiceBtn.textContent = '🛑';
                
            } catch (error) {
                console.error('Error accessing microphone:', error);
                alert('Could not access microphone. Please check permissions.');
            }
        } else {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.voiceBtn.classList.remove('active');
            this.voiceBtn.textContent = '🎤';
        }
    }
    
    sendVoiceMessage(audioBlob) {
        const reader = new FileReader();
        reader.onload = () => {
            const base64Audio = reader.result.split(',')[1];
            this.socket.emit('voice_message', { audio: base64Audio });
            this.showTypingIndicator();
        };
        reader.readAsDataURL(audioBlob);
    }
    
    playAudio(base64Audio) {
        const audio = new Audio('data:audio/mp3;base64,' + base64Audio);
        audio.play();
    }
    
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        if (file.type.startsWith('image/')) {
            this.handleImageUpload(file);
        } else if (file.type.startsWith('audio/')) {
            this.handleAudioUpload(file);
        } else {
            alert('Unsupported file type. Please upload images or audio files.');
        }
    }
    
    handleImageUpload(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.displayMessage('📷 Image uploaded', 'user');
            this.socket.emit('image_message', { 
                image: e.target.result,
                filename: file.name
            });
            this.showTypingIndicator();
        };
        reader.readAsDataURL(file);
    }
    
    handleAudioUpload(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.displayMessage('🎵 Audio uploaded', 'user');
            this.socket.emit('audio_message', { 
                audio: e.target.result,
                filename: file.name
            });
            this.showTypingIndicator();
        };
        reader.readAsDataURL(file);
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});