import speech_recognition as sr
import time
import json
from difflib import SequenceMatcher
from playsound import playsound
import os

class AudioCounter:
    def __init__(self, socketio):
        self.socketio = socketio
        self.recognizer = sr.Recognizer()
        self.reference_audio = None
        self.count = 0
        self.target_count = 10
        self.is_counting = False
        self.start_time = None
        self.similarity_threshold = 0.7
        self.config_file = 'config.json'
        self.load_config()

    def get_status(self):
        return {
            'status': 'Counting...' if self.is_counting else 'Idle',
            'reference_phrase': self.reference_audio,
            'count': self.count,
            'target_count': self.target_count,
            'similarity_threshold': self.similarity_threshold,
            'is_counting': self.is_counting
        }

    def emit_status(self):
        self.socketio.emit('update_status', self.get_status())

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.reference_audio = config.get('reference_audio')
                    self.target_count = config.get('target_count', 10)
                    self.similarity_threshold = config.get('similarity_threshold', 0.7)
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self):
        config = {
            'reference_audio': self.reference_audio,
            'target_count': self.target_count,
            'similarity_threshold': self.similarity_threshold
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    def get_similarity(self, text1, text2):
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def play_alarm(self):
        try:
            playsound('alarm.wav')
        except Exception as e:
            print(f"Error playing sound: {e}")

    def record_audio_sample(self):
        with sr.Microphone() as source:
            try:
                self.socketio.emit('update_status', {**self.get_status(), 'status': 'Adjusting for noise...'})
                self.recognizer.adjust_for_ambient_noise(source, duration=2)

                self.socketio.emit('update_status', {**self.get_status(), 'status': 'Listening for phrase...'})
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                self.reference_audio = self.recognizer.recognize_google(audio)

                self.save_config()
                self.emit_status()
                return True
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                self.emit_status() # Reset status to idle
                return False
            except Exception as e:
                print(f"Error occurred: {e}")
                self.emit_status()
                return False

    def set_target_count(self, count):
        try:
            c = int(count)
            if 1 <= c <= 999:
                self.target_count = c
                self.save_config()
        except ValueError:
            pass # Ignore invalid values from UI
        self.emit_status()

    def set_similarity_threshold(self, threshold):
        try:
            t = float(threshold)
            if 0.1 <= t <= 0.9:
                self.similarity_threshold = t
                self.save_config()
        except (ValueError, TypeError):
            pass # Ignore invalid values
        self.emit_status()

    def stop_counting(self):
        self.is_counting = False
        self.emit_status()

    def start_counting(self):
        if not self.reference_audio or self.target_count <= 0:
            return

        self.count = 0
        self.is_counting = True
        self.start_time = time.time()
        self.emit_status()

        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while self.is_counting and self.count < self.target_count:
                try:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                    recognized_text = self.recognizer.recognize_google(audio)
                    similarity = self.get_similarity(self.reference_audio, recognized_text)

                    if similarity > self.similarity_threshold:
                        self.count += 1
                        self.emit_status()

                        if self.count >= self.target_count:
                            self.play_alarm()
                            self.is_counting = False
                    else:
                        self.socketio.emit('no_match', {'recognized_text': recognized_text})

                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    continue
                except Exception as e:
                    print(f"Error during counting: {e}")
                    continue

        # Final status update after loop finishes
        self.is_counting = False
        self.emit_status()
