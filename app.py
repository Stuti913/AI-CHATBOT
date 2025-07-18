from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
from dotenv import load_dotenv
from utils.ai_handler import AIHandler
# from utils.speech_handler import SpeechHandler  # Commented out
from utils.sentiment_analyzer import SentimentAnalyzer
from models.database import db, ChatHistory
from datetime import datetime  # Added missing import

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize handlers
ai_handler = AIHandler()
# speech_handler = SpeechHandler()  # Commented out
sentiment_analyzer = SentimentAnalyzer()

# Store active users and their conversation context
active_users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    session_id = request.sid
    active_users[session_id] = {
        'context': [],
        'user_name': None,
        'preferences': {}
    }
    emit('connected', {'message': 'Connected to AI ChatBot!'})

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    if session_id in active_users:
        del active_users[session_id]

@socketio.on('user_message')
def handle_message(data):
    session_id = request.sid
    user_message = data['message']
    message_type = data.get('type', 'text')
    
    # Get user context
    user_context = active_users.get(session_id, {})
    
    # Analyze sentiment
    sentiment = sentiment_analyzer.analyze(user_message)
    
    # Generate AI response
    ai_response = ai_handler.generate_response(
        user_message, 
        user_context.get('context', []),
        sentiment
    )
    
    # Update conversation context
    user_context['context'].append({
        'user': user_message,
        'assistant': ai_response,
        'sentiment': sentiment,
        'timestamp': datetime.now().isoformat()
    })
    
    # Save to database
    chat_entry = ChatHistory(
        session_id=session_id,
        user_message=user_message,
        bot_response=ai_response,
        sentiment=sentiment
    )
    db.session.add(chat_entry)
    db.session.commit()
    
    # Emit response
    emit('bot_response', {
        'message': ai_response,
        'sentiment': sentiment,
        'typing': False
    })

# @socketio.on('voice_message')
# def handle_voice_message(data):
#     session_id = request.sid
#     
#     # Process voice input
#     try:
#         text = speech_handler.speech_to_text(data['audio'])
#         
#         # Handle the text message
#         handle_message({'message': text, 'type': 'voice'})
#         
#         # Generate voice response
#         voice_response = speech_handler.text_to_speech(
#             active_users[session_id]['context'][-1]['assistant']
#         )
#         
#         emit('voice_response', {'audio': voice_response})
#         
#     except Exception as e:
#         emit('error', {'message': 'Voice processing failed'})

@socketio.on('typing')
def handle_typing(data):
    emit('bot_typing', {'typing': True}, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)