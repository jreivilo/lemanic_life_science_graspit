from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
from collections import deque
import threading
import json
import paho.mqtt.client as mqtt
import difflib
import time
import requests
import os
import zipfile

COMMANDS = ["grasp", "release", "stop"]
MQTT_TOPIC = "/command"

# Check folder vosk if present and install when not present
if not os.path.isdir("vosk-model-en-us-0.22"):
    print("Vosk package not present ! \n\n")

    #change link and unzip
    url = 'https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip'
    print("Downloading....  \n\n")
    r = requests.get(url, allow_redirects=True)
    open('vosk-model-en-us-0.22.zip', 'wb').write(r.content)

    with zipfile.ZipFile("vosk-model-en-us-0.22.zip", 'r') as zip_ref:
        print("Unzipping vosk....  \n\n")
        zip_ref.extractall()

#model = Model("vosk-model-small-en-us-0.15")
model = Model("vosk-model-en-us-0.22")
recognizer = KaldiRecognizer(model, 16000)
audio_queue = queue.Queue()
command_deque = deque()

"""
import noisereduce as nr
import numpy as np

SAMPLE_RATE = 16000
NOISE_DURATION = 0.25 # seconds
NOISE_SAMPLE_LENGTH = int(SAMPLE_RATE * NOISE_DURATION)

noise_profile = []
noise_sample_collected = False


def audio_callback(indata, frames, time, status):
    global noise_profile, noise_sample_collected

    if status:
        print(f"Audio status: {status}")

    # Convert raw audio bytes to float32
    raw = np.frombuffer(indata, dtype=np.int16).astype(np.float32)

    # Step 1: collect noise sample
    if not noise_sample_collected:
        noise_profile.extend(raw)
        if len(noise_profile) >= NOISE_SAMPLE_LENGTH:
            noise_profile = np.array(noise_profile[:NOISE_SAMPLE_LENGTH])
            noise_sample_collected = True
            print("[INFO] Noise profile collected.")
        return  # wait until profile collected before processing

    # Step 2: denoise with the collected profile
    denoised = nr.reduce_noise(y=raw, y_noise=noise_profile, sr=SAMPLE_RATE,
                               stationary=True, prop_decrease=0.8)

    # Convert back to int16 and enqueue
    denoised_int16 = denoised.astype(np.int16).tobytes()
    audio_queue.put(denoised_int16)"""


"""def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio status: {status}")
    raw = np.frombuffer(indata, dtype=np.int16).astype(np.float32)

    # Apply noise reduction (assumes 1D mono audio)
    reduced = nr.reduce_noise(y=raw, sr=16000)

    # Convert back to int16 and enqueue
    reduced_bytes = (reduced.astype(np.int16)).tobytes()
    audio_queue.put(reduced_bytes)"""

def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio status: {status}")
    audio_queue.put(bytes(indata))


def voice_listener():
    speech_timer = None
    window_duration = 3  # seconds

    with sd.RawInputStream(samplerate=16000, blocksize=2048, dtype='int16',
                           channels=1, callback=audio_callback):
        while True:
            if recognizer.AcceptWaveform(audio_queue.get()):
                speech_timer = None
            
            now = time.monotonic()

            result = json.loads(recognizer.PartialResult())
            text = result.get("partial", "").strip().lower()

            # Start the timer if speech starts
            if text and speech_timer is None:
                speech_timer = now

            # If inside the window and text is coming, try match commands
            if speech_timer and text:
                for word in text.split():
                    best_match = difflib.get_close_matches(word, COMMANDS, n=1, cutoff=0.6)
                    if best_match:
                        cmd = best_match[0]
                        if cmd == "grasp" or cmd == "release" or cmd == "stop":
                            command_deque.append(cmd)
                            break

            # Reset recognizer after window duration
            if speech_timer and now - speech_timer > window_duration:
                recognizer.Reset()
                speech_timer = None
                continue


threading.Thread(target=voice_listener, daemon=True).start()

client = mqtt.Client()
client.connect("cluster.jolivier.ch", 1883, 60)
client.loop_start()

now = 0
state = 0
last_command_time = 0
print("Voice control system active.")


while True:
    if command_deque:
        command = command_deque.pop()
        now = time.monotonic()
        if now - last_command_time >= 3:
            if command == "grasp" and state == 0:
                last_command_time = now
                state = 1
                print(f">>> {command.upper()} command received — publishing to MQTT.")
                client.publish(MQTT_TOPIC, json.dumps({"action": command}))
            elif command == "release" and state == 1:
                last_command_time = now
                state = 2
                print(f">>> {command.upper()} command received — publishing to MQTT.")
                client.publish(MQTT_TOPIC, json.dumps({"action": command}))
            elif command == "stop" and state == 2:
                last_command_time = now
                state = 0
                print(f">>> {command.upper()} command received — publishing to MQTT.")
                client.publish(MQTT_TOPIC, json.dumps({"action": command}))
