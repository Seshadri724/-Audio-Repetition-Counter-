
**🎧 Audio Repetition Counter**

A voice-driven repetition tracker built with Python and SpeechRecognition. Ideal for counting spoken affirmations, chants, or exercises—this tool listens for a reference phrase and tracks how many times it's repeated with real-time feedback and progress visualization.

🚀 Features
- 🎤 Voice Recognition: Uses Google Speech Recognition to detect spoken phrases.
- 🔁 Repetition Tracking: Counts how many times the reference phrase is repeated.
- 📊 Progress Bar: Visual feedback with percentage and estimated time remaining.
- 🔔 Alarm Notification: Plays a celebratory sound when the target is reached.
- ⚙️ Configurable Threshold: Adjust similarity sensitivity for phrase matching.
- 🧠 Smart Matching: Uses string similarity (difflib) to tolerate minor variations.
- 🖥️ Cross-Platform Support: Works on Windows, macOS, and Linux (with minor tweaks).

🛠️ Requirements
Install dependencies using pip:
pip install SpeechRecognition


Optional (for non-Windows alarm sound):
sudo apt-get install sox



📦 File Structure

audio_counter.py       # Main script

README.md              # Project documentation



🧪 How to Use
- Run the script:
  
python audio_counter.py



- Main Menu Options:
  
- 1: Set your reference phrase (spoken once).
- 2: Set your target repetition count.
- 3: Adjust similarity threshold (default: 0.7).
- 4: Start counting repetitions.
- 5: Exit the program.
- During Counting:
- Speak your reference phrase clearly.
- Watch the progress bar update.
- Stop anytime with Ctrl+C.

🧩 Customization

- Similarity Threshold: Tune the matching sensitivity (0.1–0.9).
- Alarm Sound: Modify play_alarm() for custom audio alerts.
- Phrase Matching Logic: Enhance get_similarity() for phonetic or semantic matching.
