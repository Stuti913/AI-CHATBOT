from googletrans import Translator # type: ignore
import langdetect # type: ignore

class LanguageHandler:
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean'
        }
    
    def detect_language(self, text):
        try:
            return langdetect.detect(text)
        except:
            return 'en'
    
    def translate_text(self, text, target_lang='en', source_lang='auto'):
        try:
            if source_lang == 'auto':
                source_lang = self.detect_language(text)
            
            if source_lang == target_lang:
                return text
            
            result = self.translator.translate(text, src=source_lang, dest=target_lang)
            return result.text
        except:
            return text
    
    def get_supported_languages(self):
        return self.supported_languages