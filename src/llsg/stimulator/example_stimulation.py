import time
import llsg.driver as fes
from llsg import logger
import llsg.config as config 
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

class Stimulator():

    def __init__(self):
        self.stim: fes.Motionstim8 = fes.Motionstim8()
        self.stim.OpenSerialPort(config.SERIAL_PORT)
        self.stim.InitializeChannelListMode()
        logger.info('Opened FES serial port')
    
    def __del__(self):
        stim_code = [0, 0, 0, 0, 0, 0, 0, 0]
        self.stim.UpdateChannelSettings(stim_code)
        self.stim.CloseSerialPort()
        logger.info('Closed FES serial port')

    def stimulate(self):
        stim_code = [9, 0, 0, 0, 0, 0, 0, 0]
        self.stim.UpdateChannelSettings(stim_code)
        logger.info('FES: Sent Left')
        time.sleep(1)
        stim_code = [0, 0, 0, 0, 0, 0, 0, 0]
        self.stim.UpdateChannelSettings(stim_code)
    
    def increase_stimulate(self):
        stim_code = [5, 0, 0, 0, 0, 0, 0, 0]
        self.stim.UpdateChannelSettings(stim_code)
        logger.info('FES: Sent Left')
        time.sleep(1)
        stim_code = [0, 0, 0, 0, 0, 0, 0, 0]
        self.stim.UpdateChannelSettings(stim_code)

if __name__ == '__main__':
    threading.Thread(target=voice_listener, daemon=True).start()
    logger.info('Starting FES stimulation example')
    # Initialize the FES device
    stimulator = Stimulator()
    stimulator.stimulate()

'''
vocal_listening = True
if vocal_listening:
    print("Voice control system active.")
while True:
   command = command_queue.get()
   if command == "grasp":
    print(">>> GRASP command received — triggering stimulation.")
    stimulator.stimulate() 
   elif command == "release":
      print(">>> CLOSE command received — closing hand.")
   elif command == "stop":
    print(">>> STOP command received — stopping stimulation.")
    break
'''
del stimulator
