import speech_recognition as sr
import time
import json
from difflib import SequenceMatcher
from playsound import playsound
import os
from datetime import datetime

class AudioCounter:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.reference_audio = None
        self.count = 0
        self.target_count = 0
        self.is_counting = False
        self.start_time = None
        self.similarity_threshold = 0.7  # Configurable similarity threshold
        self.config_file = 'config.json'
        self.load_config()

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.reference_audio = config.get('reference_audio', None)
                    self.target_count = config.get('target_count', 0)
                    self.similarity_threshold = config.get('similarity_threshold', 0.7)
                    print("Configuration loaded.")
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self):
        """Save configuration to JSON file"""
        config = {
            'reference_audio': self.reference_audio,
            'target_count': self.target_count,
            'similarity_threshold': self.similarity_threshold
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        print("Configuration saved.")

    def get_similarity(self, text1, text2):
        """Calculate similarity between two strings (0-1)"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def play_alarm(self):
        """Play a standard alarm sound"""
        try:
            playsound('alarm.wav')
        except Exception as e:
            print(f"Error playing sound: {e}")
            print("\a")  # Fallback to system beep

    def show_progress(self):
        """Display progress with a visual bar"""
        progress = min(self.count / self.target_count, 1.0)
        bar_length = 30
        filled = int(bar_length * progress)
        bar = '█' * filled + '-' * (bar_length - filled)
        print(f"[{bar}] {self.count}/{self.target_count} ({progress*100:.1f}%)")

        # Calculate estimated time remaining if we have at least 1 count
        if self.count > 0 and self.start_time:
            elapsed = time.time() - self.start_time
            time_per_count = elapsed / self.count
            remaining = max(0, (self.target_count - self.count) * time_per_count)

            # Format time as MM:SS
            mins, secs = divmod(int(remaining), 60)
            print(f"Estimated time remaining: {mins:02d}:{secs:02d}")

    def record_audio_sample(self):
        """Record the reference audio sample with better feedback"""
        print("\n=== Reference Phrase Setup ===")
        print("1. Make sure you're in a quiet environment")
        print("2. Speak clearly and at a normal volume")
        print("3. You'll have 3 seconds to speak after the beep\n")

        with sr.Microphone() as source:
            try:
                print("Adjusting for ambient noise... (please stay quiet)")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Ready! Speak now...")

                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                self.reference_audio = self.recognizer.recognize_google(audio)

                print(f"\nSuccess! Reference phrase set to: '{self.reference_audio}'")
                print("Would you like to test playback? (y/n)")
                if input().lower() == 'y':
                    print("Please repeat your phrase now...")
                    test_audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    test_text = self.recognizer.recognize_google(test_audio)
                    similarity = self.get_similarity(self.reference_audio, test_text)
                    print(f"Test similarity: {similarity:.1%} - {'Good match!' if similarity > 0.6 else 'Fair match, consider re-recording'}")
                self.save_config()
                return True

            except sr.WaitTimeoutError:
                print("No speech detected during recording window")
                return False
            except sr.UnknownValueError:
                print("Could not understand the audio")
                return False
            except Exception as e:
                print(f"Error occurred: {e}")
                return False

    def set_target_count(self):
        """Enhanced target count setting with validation"""
        print("\n=== Set Target Count ===")
        print(f"Current reference phrase: '{self.reference_audio}'")

        while True:
            try:
                count = int(input("How many repetitions do you want to count? (1-999): "))
                if 1 <= count <= 999:
                    self.target_count = count
                    print(f"Target set to {count} repetitions")
                    self.save_config()
                    return
                print("Please enter a number between 1-999")
            except ValueError:
                print("Please enter a valid number")

    def start_counting(self):
        """Enhanced counting process with better feedback"""
        if not self.reference_audio:
            print("Please set a reference phrase first!")
            return

        if self.target_count <= 0:
            self.set_target_count()

        print("\n=== Counting Started ===")
        print(f"Target: {self.target_count} reps of: '{self.reference_audio}'")
        print("Press Ctrl+C at any time to stop\n")

        self.count = 0
        self.is_counting = True
        self.start_time = time.time()

        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while self.is_counting and self.count < self.target_count:
                try:
                    self.show_progress()
                    print("Listening... (speak now)")

                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                    recognized_text = self.recognizer.recognize_google(audio)
                    similarity = self.get_similarity(self.reference_audio, recognized_text)

                    if similarity > self.similarity_threshold:
                        self.count += 1
                        print(f"✓ Match #{self.count}: '{recognized_text}' ({similarity:.1%})")

                        if self.count >= self.target_count:
                            total_time = time.time() - self.start_time
                            mins, secs = divmod(int(total_time), 60)
                            print(f"\n🎉 TARGET REACHED IN {mins:02d}:{secs:02d}! 🎉")
                            self.play_alarm()
                            self.is_counting = False
                    else:
                        print(f"✗ No match: '{recognized_text}' ({similarity:.1%})")

                except sr.WaitTimeoutError:
                    print("(Listening timed out - try speaking louder)")
                    continue
                except sr.UnknownValueError:
                    print("(Audio not understood - try speaking clearer)")
                    continue
                except KeyboardInterrupt:
                    self.is_counting = False
                    print("\nCounting stopped by user")
                except Exception as e:
                    print(f"(Error: {e})")
                    continue

    def run(self):
        """Main program loop with enhanced interface"""
        print("\n" + "="*40)
        print("🎧 AUDIO REPETITION COUNTER".center(40))
        print("="*40)

        while True:
            print("\nMain Menu:")
            print("1. 🎤 Set reference phrase")
            print("2. 🔢 Set target count")
            print("3. ⚙️ Adjust settings")
            print("4. ▶️ Start counting")
            print("5. ❌ Exit")

            choice = input("\nChoose an option (1-5): ").strip()

            if choice == "1":
                if not self.record_audio_sample():
                    print("Failed to set reference phrase. Try again?")
            elif choice == "2":
                self.set_target_count()
            elif choice == "3":
                print(f"\nCurrent similarity threshold: {self.similarity_threshold}")
                try:
                    new_thresh = float(input("Enter new threshold (0.1-0.9): "))
                    if 0.1 <= new_thresh <= 0.9:
                        self.similarity_threshold = new_thresh
                        print(f"Threshold set to {new_thresh}")
                        self.save_config()
                    else:
                        print("Value must be between 0.1-0.9")
                except ValueError:
                    print("Invalid number")
            elif choice == "4":
                self.start_counting()

                # Show final results
                print("\n" + "="*40)
                print("FINAL RESULTS".center(40))
                print("="*40)
                print(f"Reference phrase: '{self.reference_audio}'")
                print(f"Target count:     {self.target_count}")
                print(f"Actual count:     {self.count}")

                if self.start_time:
                    total_time = time.time() - self.start_time
                    mins, secs = divmod(int(total_time), 60)
                    print(f"Total time:       {mins:02d}:{secs:02d}")
                    if self.count > 0:
                        print(f"Average pace:     {total_time/self.count:.1f} sec per rep")

                print("="*40)
                input("\nPress Enter to continue...")

            elif choice == "5":
                print("\nThank you for using the Audio Counter! Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    try:
        counter = AudioCounter()
        counter.run()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        input("Press Enter to exit...")
