import speech_recognition as sr
import pydub
from gtts import gTTS
import pygame
import io
import base64
import tempfile
import os

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()
    
    def speech_to_text(self, audio_data):
        try:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            # Convert to text
            with sr.AudioFile(tmp_file_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
            
            # Clean up
            os.unlink(tmp_file_path)
            
            return text
            
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio"
        except Exception as e:
            return f"Error processing audio: {str(e)}"
    
    def text_to_speech(self, text):
        try:
            tts = gTTS(text=text, lang='en')
            
            # Save to bytes
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            # Convert to base64
            audio_base64 = base64.b64encode(fp.read()).decode('utf-8')
            
            return audio_base64
            
        except Exception as e:
            return None