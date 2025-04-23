import paho.mqtt.client as mqtt
import json
import llsg.stimulator.driver as fes
from llsg import logger
import llsg.config as config
import math
import time

class Stimulator:
    def __init__(self):
        # Initialize FES device
        self.stim = fes.Motionstim8()
        self.stim.OpenSerialPort(config.SERIAL_PORT)
        self.stim.InitializeChannelListMode()
        logger.info('Opened FES serial port')
        
        # Initialize objectives and current state
        self.objective_angle = 0.0
        self.current_angle = 0.0
        self.previous_angle_timestamp = 0
        self.previous_intensity = 0
        
        # Command to channel mapping
        self.command_channel_map = {
            "grasp": [0, 3],  # Channel 1 (index 0)
            "release": [2]   # Channel 3 (index 2)
        }
        
        # Current active command
        self.active_command = None
        self.alpha = 0.2
        self.beta = 0.2

    def __del__(self):
        # Turn off all stimulation when object is destroyed
        stim_code = [0, 0, 0, 0, 0, 0, 0, 0]
        self.stim.UpdateChannelSettings(stim_code)
        self.stim.CloseSerialPort()
        logger.info('Closed FES serial port')
    
    def stimulate(self, intensity, command="grasp"):
        # Create a stimulation code array with all zeros
        stim_code = [0, 0, 0, 0, 0, 0, 0, 0]
        
        # Set the intensity for the appropriate channel
        channels = self.command_channel_map.get(command, 0)
        for channel in channels:
            if channel == 3:
                intensity = min(3, intensity)
            stim_code[channel] = int(intensity)
        
        # Apply stimulation
        self.stim.UpdateChannelSettings(stim_code)
        logger.info(f'FES: Stimulating channel {channel+1} with intensity {intensity}')
        
    def calculate_stimulation_intensity(self):
        # Calculate error between current and objective angle
        error = abs(self.objective_angle - self.current_angle)
        
        intensity = self.previous_intensity + self.alpha * error + self.beta
        self.previous_intensity = intensity
        
        # Ensure intensity is within valid range
        intensity = max(0, min(7, intensity)) # mA
        logger.info(f'Calculated stimulation intensity: {intensity} for error: {error}')
        
        return intensity
    
    def process_command(self, command):
        if command == "grasp":
            self.objective_angle = 3.14
            self.active_command = "grasp"
            logger.info("Command received: grasp - Setting objective angle to 3.14")
        elif command == "release":
            self.objective_angle = 0.2
            self.active_command = "release"
            logger.info("Command received: release - Setting objective angle to 0.0")
        elif command == "pinch":
            self.objective_angle = 1.57
            self.active_command = "pinch"
            logger.info("Command received: pinch - Setting objective angle to 1.57")
        
    def update_sensor_reading(self, angle, timestamp):
        if timestamp - self.previous_angle_timestamp < 100:
            # Ignore readings that are too close together
            return

        self.previous_angle_timestamp = timestamp
        self.current_angle = angle
        
        # Only stimulate if we have an active command
        if self.active_command:
            intensity = self.calculate_stimulation_intensity()
            self.stimulate(intensity, self.active_command)

def main():
    stimulator = Stimulator()
    
    # Callback when connected to broker
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribe to both sensor and command topics
        client.subscribe("/sensor")
        client.subscribe("/command")

    # Callback when a message is received
    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            print(f"Received message on topic {msg.topic}: {payload}")
            
            if msg.topic == "/sensor":
                if "grasp_angle" in payload:
                    stimulator.update_sensor_reading(payload["grasp_angle"], payload["timestamp_ms"])
            
            elif msg.topic == "/command":
                if "action" in payload:
                    stimulator.process_command(payload["action"])
                    
        except json.JSONDecodeError:
            print(f"Error decoding JSON from message: {msg.payload.decode()}")
        except Exception as e:
            print(f"Error processing message: {e}")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect("cluster.jolivier.ch", 1883, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("Stimulator stopped by user")
    finally:
        # Ensure stimulator is properly closed
        del stimulator


if __name__ == "__main__":
    main()