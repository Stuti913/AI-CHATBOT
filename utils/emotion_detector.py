import re
from textblob import TextBlob # type: ignore

class EmotionDetector:
    def __init__(self):
        self.emotion_patterns = {
            'joy': ['happy', 'excited', 'great', 'awesome', 'wonderful', 'fantastic'],
            'sadness': ['sad', 'depressed', 'down', 'upset', 'disappointed'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'irritated'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous'],
            'surprise': ['surprised', 'amazed', 'shocked', 'stunned'],
            'disgust': ['disgusted', 'revolted', 'sick', 'gross']
        }
    
    def detect_emotion(self, text):
        text_lower = text.lower()
        emotions_detected = []
        
        for emotion, patterns in self.emotion_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                emotions_detected.append(emotion)
        
        # Use TextBlob for additional sentiment analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            emotions_detected.append('joy')
        elif polarity < -0.1:
            emotions_detected.append('sadness')
        
        return emotions_detected if emotions_detected else ['neutral']
    
    def get_appropriate_response_tone(self, emotions):
        if 'sadness' in emotions:
            return 'empathetic'
        elif 'anger' in emotions:
            return 'calming'
        elif 'joy' in emotions:
            return 'enthusiastic'
        elif 'fear' in emotions:
            return 'reassuring'
        else:
            return 'neutral'