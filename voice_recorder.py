import sounddevice as sd
import numpy as np
import wavio
from datetime import datetime

# Settings
SAMPLE_RATE = 44100
CHANNELS = 1
THRESHOLD = 1.6           # Increase if silence is not detected
SILENCE_DURATION = 3
CHUNK_DURATION = 0.5
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION)
DEVICE_INDEX = None  # Set your mic index if needed

def record_until_silence():
    print("Recording... Speak now.")

    recorded = []
    silent_chunks = 0

    with sd.InputStream(device=DEVICE_INDEX,
                        samplerate=SAMPLE_RATE,
                        channels=CHANNELS,
                        dtype='float32') as stream:
        while True:
            audio_chunk, _ = stream.read(CHUNK_SAMPLES)
            volume = np.linalg.norm(audio_chunk)
            print(f"Volume: {volume:.4f}")  # Debug output

            recorded.append(audio_chunk)

            if volume < THRESHOLD:
                silent_chunks += 1
            else:
                silent_chunks = 0

            if silent_chunks * CHUNK_DURATION >= SILENCE_DURATION:
                print("Silence detected. Stopping recording.")
                break

    audio_data = np.concatenate(recorded, axis=0)
    file_name = f"user_audio_to_text_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp3"
    wavio.write(file_name, audio_data, SAMPLE_RATE, sampwidth=2)
    print(f"✅ Saved recording to {file_name}.")
    return file_name