import json
from datetime import datetime, timedelta

class MemoryManager:
    def __init__(self):
        self.short_term_memory = {}
        self.long_term_memory = {}
        self.user_profiles = {}
    
    def store_conversation(self, session_id, user_message, bot_response):
        if session_id not in self.short_term_memory:
            self.short_term_memory[session_id] = []
        
        self.short_term_memory[session_id].append({
            'user': user_message,
            'bot': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 20 exchanges
        if len(self.short_term_memory[session_id]) > 20:
            self.short_term_memory[session_id] = self.short_term_memory[session_id][-20:]
    
    def get_conversation_context(self, session_id, limit=5):
        if session_id not in self.short_term_memory:
            return []
        return self.short_term_memory[session_id][-limit:]
    
    def update_user_profile(self, session_id, profile_data):
        self.user_profiles[session_id] = profile_data
    
    def get_user_profile(self, session_id):
        return self.user_profiles.get(session_id, {})