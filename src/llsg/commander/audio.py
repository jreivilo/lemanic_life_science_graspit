from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import threading
import json
import paho.mqtt.client as mqtt

COMMANDS = ["grasp", "release"]
MQTT_TOPIC = "/command"
CONFIDENCE_THRESHOLD = 0.3

model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000, json.dumps(COMMANDS))
audio_queue = queue.Queue()
command_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio status: {status}")
    audio_queue.put(bytes(indata))

"""def voice_listener():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip().lower()
                if text in COMMANDS:
                    dict = {}
                    dict["action"] = str(text)
                    res = json.dumps(dict)
                    command_queue.put(res)"""

def voice_listener():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip().lower()

                if text in COMMANDS:
                    word_confs = [entry["conf"] for entry in result.get("result", []) if entry["word"] == text]

                    if word_confs:
                        if min(word_confs) >= CONFIDENCE_THRESHOLD:
                            payload = json.dumps({"action": text})
                            command_queue.put(payload)
                        else:
                            print(f"Ignored '{text}' due to low confidence: {word_confs}")
                    else:
                        # No word-level confidence returned, fallback to trusting the grammar match
                        print(f"No confidence info for '{text}', accepting based on grammar.")
                        payload = json.dumps({"action": text})
                        command_queue.put(payload)


threading.Thread(target=voice_listener, daemon=True).start()

client = mqtt.Client()
client.connect("cluster.jolivier.ch", 1883, 60)
client.loop_start()  

print("Voice control system active.")
while True:
    command = command_queue.get()
    print(f">>> {command.upper()} command received — publishing to MQTT.")
    client.publish(MQTT_TOPIC, command)
