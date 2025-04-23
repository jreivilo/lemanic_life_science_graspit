from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import threading
import json


COMMANDS = ["grasp", "release", "stop"]
model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000, json.dumps(COMMANDS))
audio_queue = queue.Queue()
command_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
   if status:
       pass
   audio_queue.put(bytes(indata))


def voice_listener():
   with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                          channels=1, callback=audio_callback):
       while True:
           data = audio_queue.get()
           if recognizer.AcceptWaveform(data):
               result = json.loads(recognizer.Result())
               text = result.get("text", "").strip().lower()
               if text in COMMANDS:
                   command_queue.put(text)

# Start listener in background
threading.Thread(target=voice_listener, daemon=True).start()

# Main logic: reacts to commands
print("Voice control system active.")
while True:
   command = command_queue.get()
   if command == "grasp":
       print(">>> GRASP command received — triggering stimulation.")
   elif command == "release":
       print(">>> CLOSE command received — closing hand.")
   elif command == "stop":
       break