import json
import os
from datetime import datetime

class KnowledgeBase:
    def __init__(self):
        self.knowledge_file = 'knowledge_base.json'
        self.knowledge = self.load_knowledge()
    
    def load_knowledge(self):
        if os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_knowledge(self):
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def add_knowledge(self, topic, information):
        self.knowledge[topic] = {
            'info': information,
            'timestamp': datetime.now().isoformat(),
            'usage_count': 0
        }
        self.save_knowledge()
    
    def get_knowledge(self, topic):
        if topic in self.knowledge:
            self.knowledge[topic]['usage_count'] += 1
            self.save_knowledge()
            return self.knowledge[topic]['info']
        return None
    
    def search_knowledge(self, query):
        results = []
        query_lower = query.lower()
        
        for topic, data in self.knowledge.items():
            if query_lower in topic.lower() or query_lower in data['info'].lower():
                results.append({
                    'topic': topic,
                    'info': data['info'],
                    'relevance': self._calculate_relevance(query_lower, topic, data['info'])
                })
        
        return sorted(results, key=lambda x: x['relevance'], reverse=True)
    
    def _calculate_relevance(self, query, topic, info):
        score = 0
        if query in topic.lower():
            score += 10
        if query in info.lower():
            score += 5
        
        # Count word matches
        query_words = query.split()
        topic_words = topic.lower().split()
        info_words = info.lower().split()
        
        for word in query_words:
            if word in topic_words:
                score += 3
            if word in info_words:
                score += 1
        
        return score