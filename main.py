import os
from src.Audio_Counter import AudioCounter
from generate_alarm import generate_alarm_sound

if __name__ == "__main__":
    if not os.path.exists('alarm.wav'):
        print("Generating alarm sound...")
        generate_alarm_sound()

    try:
        counter = AudioCounter()
        counter.run()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        input("Press Enter to exit...")
