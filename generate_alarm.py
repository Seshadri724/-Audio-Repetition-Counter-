import numpy as np
from scipy.io.wavfile import write

def generate_alarm_sound(filename="alarm.wav", duration=1.0, frequency=1000, sample_rate=44100):
    """Generates a simple sine wave alarm sound and saves it as a WAV file."""
    t = np.linspace(0., duration, int(sample_rate * duration))
    amplitude = np.iinfo(np.int16).max * 0.5
    data = amplitude * np.sin(2. * np.pi * frequency * t)
    write(filename, sample_rate, data.astype(np.int16))
    print(f"Generated '{filename}' successfully.")

if __name__ == "__main__":
    generate_alarm_sound()
