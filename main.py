import os
import sys
from datetime import datetime
import logging
from dotenv import dotenv_values # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from groq import Groq # type: ignore
    from flask import Flask, render_template_string, request # type: ignore
    from flask_socketio import SocketIO, emit # type: ignore
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required packages: pip install groq flask flask-socketio python-dotenv")
    sys.exit(1)

# Load environment variables
env_vars = dotenv_values(".env")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Get environment variables
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Check if API key is loaded properly
if not GroqAPIKey:
    print("❌ GroqAPIKey not found in .env file")
    sys.exit(1)

if not Username:
    print("⚠ Username not found in .env file, using default")
    Username = "User"

if not Assistantname:
    print("⚠ Assistantname not found in .env file, using default")
    Assistantname = "AI Assistant"

# Store conversation history
conversations = {}

class GroqChatBot:
    def __init__(self):
        # Initialize Groq client
        try:
            self.client = Groq(api_key=GroqAPIKey)
            print("✅ Groq API client initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Groq client: {e}")
            sys.exit(1)
        
        # System message template
        self.system_message = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***"""
    
    def get_ai_response(self, user_message, user_id):
        try:
            print(f"📨 Processing message: {user_message[:50]}...")
            
            # Add user message to history
            if user_id not in conversations:
                conversations[user_id] = []
            
            conversations[user_id].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Prepare messages for Groq
            messages = [
                {"role": "system", "content": self.system_message}
            ]
            
            # Add recent conversation history (limited for context)
            recent_messages = conversations[user_id][-5:]  # Last 5 messages for context
            for msg in recent_messages:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            print(f"🔄 Making Groq API request...")
            
            # Make API call to Groq
            ai_message = self.make_groq_api_call(messages)
            
            print(f"✅ Received response: {ai_message[:50]}...")
            
            # Add AI response to history
            conversations[user_id].append({
                "role": "assistant",
                "content": ai_message,
                "timestamp": datetime.now().isoformat()
            })
            
            return ai_message
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error: {error_msg}")
            logger.error(f"Chatbot error: {error_msg}")
            
            if "rate" in error_msg.lower() or "limit" in error_msg.lower():
                return "⏰ Rate limit exceeded. Please wait and try again."
            elif "quota" in error_msg.lower():
                return "💳 API quota exceeded. Please check your account."
            elif "API key" in error_msg:
                return "🔑 API key error. Please check your configuration."
            else:
                return f"❌ Sorry, there was an error: {error_msg}"
    
    def make_groq_api_call(self, messages):
        """Make API call to Groq"""
        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",  # Fast Groq model
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Groq API call failed: {e}")
            raise e

# Initialize chatbot
print("🤖 Initializing Groq chatbot...")
chatbot = GroqChatBot()

# Modern HTML template with contemporary design
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ assistantname }} - Advanced AI Chat</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            --secondary-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --dark-bg: #0f0f23;
            --card-bg: rgba(255, 255, 255, 0.95);
            --glass-bg: rgba(255, 255, 255, 0.1);
            --text-primary: #2d3748;
            --text-secondary: #718096;
            --border-color: rgba(255, 255, 255, 0.2);
            --success-color: #48bb78;
            --error-color: #f56565;
            --shadow-light: 0 20px 60px rgba(0, 0, 0, 0.1);
            --shadow-heavy: 0 30px 80px rgba(0, 0, 0, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--dark-bg);
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 80%, rgba(120, 219, 226, 0.3) 0%, transparent 50%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            overflow: hidden;
            animation: backgroundShift 20s ease-in-out infinite alternate;
        }

        @keyframes backgroundShift {
            0% {
                background-position: 0% 0%, 100% 100%, 50% 50%;
            }
            100% {
                background-position: 100% 100%, 0% 0%, 25% 75%;
            }
        }

        .chat-container {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            box-shadow: var(--shadow-heavy);
            width: 100%;
            max-width: 900px;
            height: 90vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
            animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(60px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .chat-header {
            background: var(--primary-gradient);
            padding: 25px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .chat-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
            transform: rotate(45deg);
            animation: shimmer 3s linear infinite;
        }

        @keyframes shimmer {
            0% { transform: translateX(-100%) rotate(45deg); }
            100% { transform: translateX(100%) rotate(45deg); }
        }

        .chat-header-content {
            position: relative;
            z-index: 2;
        }

        .chat-header h1 {
            font-size: 2rem;
            font-weight: 700;
            color: white;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }

        .ai-icon {
            width: 40px;
            height: 40px;
            background: rgba(255,255,255,0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        .status {
            font-size: 0.95rem;
            color: rgba(255,255,255,0.9);
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            background: var(--success-color);
            border-radius: 50%;
            animation: statusPulse 2s ease-in-out infinite;
        }

        @keyframes statusPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .chat-messages {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
            background: transparent;
            scroll-behavior: smooth;
        }

        .message {
            margin-bottom: 25px;
            display: flex;
            align-items: flex-end;
            gap: 12px;
            animation: messageSlide 0.5s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes messageSlide {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            flex-direction: row-reverse;
        }

        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            font-weight: 600;
            flex-shrink: 0;
        }

        .message.ai .message-avatar {
            background: var(--secondary-gradient);
            color: white;
        }

        .message.user .message-avatar {
            background: var(--primary-gradient);
            color: white;
        }

        .message-bubble {
            max-width: 70%;
            position: relative;
        }

        .message-content {
            padding: 16px 22px;
            border-radius: 18px;
            position: relative;
            word-wrap: break-word;
            line-height: 1.5;
            font-size: 0.95rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }

        .message.user .message-content {
            background: var(--primary-gradient);
            color: white;
            border-bottom-right-radius: 6px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }

        .message.ai .message-content {
            background: var(--card-bg);
            color: var(--text-primary);
            border-bottom-left-radius: 6px;
            box-shadow: var(--shadow-light);
        }

        .message-time {
            font-size: 0.75rem;
            color: rgba(255,255,255,0.7);
            margin-top: 6px;
            text-align: right;
        }

        .message.ai .message-time {
            color: var(--text-secondary);
            text-align: left;
        }

        .typing-indicator {
            display: none;
            padding: 20px 30px;
            color: rgba(255,255,255,0.8);
            font-style: italic;
        }

        .typing-indicator.show {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
        }

        .typing-dots span {
            width: 8px;
            height: 8px;
            background: var(--secondary-gradient);
            border-radius: 50%;
            animation: typingDots 1.4s ease-in-out infinite both;
        }

        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes typingDots {
            0%, 80%, 100% {
                transform: scale(0);
            }
            40% {
                transform: scale(1);
            }
        }

        .chat-input-container {
            padding: 25px 30px;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border-top: 1px solid var(--border-color);
        }

        .input-wrapper {
            display: flex;
            gap: 12px;
            align-items: center;
            background: var(--card-bg);
            border-radius: 50px;
            padding: 8px 8px 8px 24px;
            box-shadow: var(--shadow-light);
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .input-wrapper:focus-within {
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3), var(--shadow-light);
            border-color: rgba(102, 126, 234, 0.5);
        }

        #messageInput {
            flex: 1;
            border: none;
            outline: none;
            font-size: 1rem;
            background: transparent;
            color: var(--text-primary);
            padding: 12px 0;
        }

        #messageInput::placeholder {
            color: var(--text-secondary);
        }

        .action-buttons {
            display: flex;
            gap: 8px;
        }

        .btn {
            border: none;
            border-radius: 50px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            transform: translate(-50%, -50%);
        }

        .btn:hover::before {
            width: 120%;
            height: 120%;
        }

        .btn:active {
            transform: scale(0.95);
        }

        #sendButton {
            background: var(--secondary-gradient);
            color: white;
            padding: 12px 20px;
            box-shadow: 0 4px 20px rgba(79, 172, 254, 0.3);
        }

        #sendButton:hover {
            box-shadow: 0 8px 30px rgba(79, 172, 254, 0.4);
            transform: translateY(-2px);
        }

        #sendButton:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        #clearButton {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
            color: white;
            padding: 12px 16px;
            box-shadow: 0 4px 20px rgba(255, 107, 107, 0.3);
        }

        #clearButton:hover {
            box-shadow: 0 8px 30px rgba(255, 107, 107, 0.4);
            transform: translateY(-2px);
        }

        .chat-info {
            text-align: center;
            padding: 15px;
            font-size: 0.85rem;
            color: rgba(255,255,255,0.7);
            background: rgba(255,255,255,0.03);
        }

        .powered-by {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        /* Custom scrollbar */
        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }

        .chat-messages::-webkit-scrollbar-track {
            background: transparent;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.3);
            border-radius: 10px;
        }

        .chat-messages::-webkit-scrollbar-thumb:hover {
            background: rgba(255,255,255,0.5);
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .chat-container {
                height: 95vh;
                border-radius: 16px;
                max-width: none;
            }
            
            .chat-header {
                padding: 20px;
            }
            
            .chat-header h1 {
                font-size: 1.6rem;
            }
            
            .chat-messages {
                padding: 20px;
            }
            
            .message-bubble {
                max-width: 85%;
            }
            
            .chat-input-container {
                padding: 20px;
            }
            
            .action-buttons {
                flex-direction: column;
            }
            
            .btn {
                padding: 10px 16px;
            }
        }

        /* Loading animation */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .fade-in {
            animation: fadeIn 0.5s ease-in-out;
        }

        /* Connection status styles */
        .status.connected {
            color: var(--success-color);
        }

        .status.error {
            color: var(--error-color);
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="chat-header-content">
                <h1>
                    <div class="ai-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    {{ assistantname }}
                </h1>
                <div id="status" class="status">
                    <div class="status-indicator"></div>
                    <span>Connecting...</span>
                </div>
            </div>
        </div>
        
        <div id="chat-messages" class="chat-messages">
            <div class="message ai fade-in">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-bubble">
                    <div class="message-content">
                        🚀 Hey there! I'm {{ assistantname }}, your advanced AI assistant. I'm here to help you with anything you need. What would you like to explore today?
                    </div>
                </div>
            </div>
        </div>
        
        <div id="typing" class="typing-indicator">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span>{{ assistantname }} is thinking...</span>
        </div>
        
        <div class="chat-input-container">
            <div class="input-wrapper">
                <input type="text" id="messageInput" placeholder="Ask me anything..." maxlength="500">
                <div class="action-buttons">
                    <button id="sendButton" class="btn">
                        <i class="fas fa-paper-plane"></i>
                        Send
                    </button>
                    <button id="clearButton" class="btn">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
        
        <div class="chat-info">
            <div class="powered-by">
                <i class="fas fa-bolt"></i>
                <span>Powered by Groq Lightning Fast AI</span>
                <i class="fas fa-brain"></i>
            </div>
        </div>
    </div>

    <script>
        // Initialize Socket.IO connection
        const socket = io();
        
        // DOM elements
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const clearButton = document.getElementById('clearButton');
        const chatMessages = document.getElementById('chat-messages');
        const statusDiv = document.getElementById('status');
        const typingDiv = document.getElementById('typing');
        
        // Socket event handlers
        socket.on('connect', function() {
            console.log('✅ Connected to server');
            updateStatus('Connected & Ready', 'connected');
        });
        
        socket.on('status', function(data) {
            updateStatus(data.msg, 'connected');
        });
        
        socket.on('ai_response', function(data) {
            hideTyping();
            addMessage(data.message, 'ai', data.timestamp);
            enableSending();
        });
        
        // Functions
        function sendMessage() {
            const message = messageInput.value.trim();
            if (message === '') return;
            
            // Add user message to chat
            addMessage(message, 'user');
            
            // Clear input and disable sending
            messageInput.value = '';
            disableSending();
            showTyping();
            
            // Send message to server
            socket.emit('user_message', {message: message});
        }
        
        function addMessage(content, sender, timestamp = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender} fade-in`;
            
            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'message-avatar';
            avatarDiv.innerHTML = sender === 'ai' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
            
            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'message-bubble';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            bubbleDiv.appendChild(contentDiv);
            
            if (timestamp) {
                const timeDiv = document.createElement('div');
                timeDiv.className = 'message-time';
                timeDiv.textContent = timestamp;
                bubbleDiv.appendChild(timeDiv);
            }
            
            messageDiv.appendChild(avatarDiv);
            messageDiv.appendChild(bubbleDiv);
            
            chatMessages.appendChild(messageDiv);
            scrollToBottom();
        }
        
        function clearChat() {
            chatMessages.innerHTML = `
                <div class="message ai fade-in">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-bubble">
                        <div class="message-content">
                            🚀 Chat cleared! I'm {{ assistantname }}, ready to help you again. What can I do for you?
                        </div>
                    </div>
                </div>
            `;
        }
        
        function scrollToBottom() {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function disableSending() {
            sendButton.disabled = true;
            sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            messageInput.disabled = true;
        }
        
        function enableSending() {
            sendButton.disabled = false;
            sendButton.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
            messageInput.disabled = false;
            messageInput.focus();
        }
        
        function showTyping() {
            typingDiv.classList.add('show');
            scrollToBottom();
        }
        
        function hideTyping() {
            typingDiv.classList.remove('show');
        }
        
        function updateStatus(message, type = '') {
            const statusSpan = statusDiv.querySelector('span');
            statusSpan.textContent = message;
            statusDiv.className = `status ${type}`;
        }
        
        // Event listeners
        sendButton.addEventListener('click', sendMessage);
        clearButton.addEventListener('click', clearChat);
        
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !sendButton.disabled) {
                sendMessage();
            }
        });
        
        messageInput.addEventListener('input', function() {
            const charCount = this.value.length;
            const wrapper = this.closest('.input-wrapper');
            if (charCount > 450) {
                wrapper.style.borderColor = '#ff6b6b';
            } else {
                wrapper.style.borderColor = 'rgba(255,255,255,0.2)';
            }
        });
        
        // Focus on input when page loads
        window.addEventListener('load', function() {
            messageInput.focus();
        });
        
        // Handle connection errors
        socket.on('connect_error', function() {
            updateStatus('Connection Failed', 'error');
        });
        
        socket.on('disconnect', function() {
            updateStatus('Disconnected', 'error');
        });
        
        // Auto-resize input based on content
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, assistantname=Assistantname)

@socketio.on('connect')
def handle_connect():
    print(f'✅ User connected: {request.sid}')
    emit('status', {'msg': f'Connected to {Assistantname}!'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'❌ User disconnected: {request.sid}')

@socketio.on('user_message')
def handle_message(data):
    user_message = data['message']
    user_id = request.sid
    
    print(f'📨 Message from {user_id}: {user_message}')
    
    # Get AI response
    ai_response = chatbot.get_ai_response(user_message, user_id)
    
    # Send response back to client
    emit('ai_response', {
        'message': ai_response,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    })

if __name__ == '__main__':
    print("🚀 Starting Groq AI Chatbot...")
    print(f"🤖 Assistant Name: {Assistantname}")
    print(f"👤 User Name: {Username}")
    print("🌐 Access at: http://localhost:5000")
    
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Server error: {e}")
        input("Press Enter to exit...")