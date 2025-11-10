import os
from flask import Flask, render_template
from flask_socketio import SocketIO
from src.Audio_Counter import AudioCounter
from generate_alarm import generate_alarm_sound

app = Flask(__name__)
socketio = SocketIO(app)

if not os.path.exists('alarm.wav'):
    print("Generating alarm sound...")
    generate_alarm_sound()

counter = AudioCounter(socketio)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    counter.emit_status()

@socketio.on('set_phrase')
def handle_set_phrase():
    socketio.start_background_task(counter.record_audio_sample)

@socketio.on('start_counting')
def handle_start_counting(data):
    counter.set_target_count(data.get('target_count'))
    counter.set_similarity_threshold(data.get('similarity_threshold'))
    socketio.start_background_task(counter.start_counting)

@socketio.on('stop_counting')
def handle_stop_counting():
    counter.stop_counting()

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
