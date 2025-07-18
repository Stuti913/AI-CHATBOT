import openai
import os
from datetime import datetime
import json

class AIHandler:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.conversation_memory = {}
        self.personality = {
            'name': 'AI Assistant',
            'traits': ['helpful', 'friendly', 'knowledgeable', 'patient'],
            'expertise': ['general knowledge', 'problem solving', 'creative tasks']
        }
    
    def generate_response(self, user_message, context, sentiment):
        try:
            # Build conversation history
            messages = self._build_conversation_history(user_message, context, sentiment)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.6,
                frequency_penalty=0.6
            )
            
            ai_response = response.choices[0].message.content
            
            # Apply personality and context awareness
            ai_response = self._apply_personality(ai_response, sentiment)
            
            return ai_response
            
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"
    
    def _build_conversation_history(self, user_message, context, sentiment):
        system_message = f"""You are {self.personality['name']}, an advanced AI assistant with the following traits: {', '.join(self.personality['traits'])}.
        
        Current user sentiment: {sentiment}
        
        Instructions:
        - Maintain context from previous conversations
        - Adapt your tone based on user sentiment
        - Provide helpful, accurate, and engaging responses
        - Ask follow-up questions when appropriate
        - Remember user preferences and past interactions
        """
        
        messages = [{"role": "system", "content": system_message}]
        
        # Add recent context
        for ctx in context[-5:]:  # Last 5 exchanges
            messages.append({"role": "user", "content": ctx['user']})
            messages.append({"role": "assistant", "content": ctx['assistant']})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _apply_personality(self, response, sentiment):
        if sentiment == 'negative':
            response = "I understand you might be feeling frustrated. " + response
        elif sentiment == 'positive':
            response = "I'm glad you're feeling positive! " + response
        
        return response