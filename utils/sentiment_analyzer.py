import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import re

class SentimentAnalyzer:
    def __init__(self):
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
        
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze(self, text):
        # Clean text
        cleaned_text = re.sub(r'[^\w\s]', '', text)
        
        # Get sentiment scores
        scores = self.analyzer.polarity_scores(cleaned_text)
        
        # Determine overall sentiment
        if scores['compound'] >= 0.05:
            return 'positive'
        elif scores['compound'] <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def get_detailed_sentiment(self, text):
        scores = self.analyzer.polarity_scores(text)
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }