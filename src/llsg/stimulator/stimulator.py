import json
import math
import os
import time

import numpy as np
import paho.mqtt.client as mqtt

import llsg.config as config
import llsg.stimulator.driver as fes
from llsg import logger


class Stimulator:
    def __init__(self):
        # Initialize FES device
        self.stim = fes.Motionstim8()
        self.stim.OpenSerialPort(config.SERIAL_PORT)
        self.stim.InitializeChannelListMode()
        logger.info("Opened FES serial port")

        # Initialize objectives and current state
        self.objective_angle = 0.0
        self.current_angle = 0.0
        self.previous_angle_timestamp = 0
        self.previous_intensity = 0
        self.is_rec = False

        # Command to channel mapping
        self.command_channel_map = {
            "grasp": [0],  # Channel 1 (index 0)
            "release": [2],  # Channel 3 (index 2)
            "calibration": [2],
        }

        # Current active command
        self.active_command = None
        self.error = 0

        calibration_data = np.loadtxt("calibration_set_grasp.txt")
        angles = calibration_data[:, 1]
        currents = calibration_data[:, 0]
        coeffs = np.polyfit(angles, currents, 1)
        self.alpha_grasp, self.beta_grasp = coeffs

        calibration_data = np.loadtxt("calibration_set_release.txt")
        angles = calibration_data[:, 1]
        currents = calibration_data[:, 0]
        coeffs = np.polyfit(angles, currents, 1)
        self.alpha_release, self.beta_release = coeffs

        self.calibration_intensities = [
            0,
            0,
            5,
            0,
            6,
            0,
            7,
            0,
            8,
            0,
            9,
            0,
            5,
            6,
            7,
            8,
            9,
            0,
        ]
        self.intensity_idx = 0
        self.intensity = 0

    def __del__(self):
        # Turn off all stimulation when object is destroyed
        stim_code = [0, 0, 0, 0, 0, 0, 0, 0]
        self.stim.UpdateChannelSettings(stim_code)
        time.sleep(1)
        self.stim.CloseSerialPort()
        logger.info("Closed FES serial port")

    def stimulate(self, intensity, command="grasp"):
        # Create a stimulation code array with all zeros
        stim_code = [0, 0, 0, 0, 0, 0, 0, 0]

        # Set the intensity for the appropriate channel
        channels = self.command_channel_map.get(command, 0)
        for channel in channels:
            if channel == 3:
                intensity = min(7, intensity)
            stim_code[channel] = int(intensity)

        # Apply stimulation
        self.stim.UpdateChannelSettings(stim_code)
        logger.info(f"FES: Stimulating channel {channel+1} with intensity {intensity}")

    def calculate_stimulation_intensity(self):
        # Calculate error between current and objective angle
        if self.objective_angle is None:
            self.error = 0
        else:
            self.error = abs(self.objective_angle - self.current_angle)

        intensity = self.previous_intensity + self.alpha * self.error + self.beta
        self.previous_intensity = intensity

        # Ensure intensity is within valid range
        intensity = min(9, max(0, intensity))  # mA
        logger.info(
            f"Calculated stimulation intensity: {intensity} for error: {self.error}"
        )

        return intensity

    def process_command(self, command):
        if command == "grasp":
            self.objective_angle = 3.14
            self.active_command = "grasp"
            self.alpha = self.alpha_grasp
            self.beta = self.beta_grasp
            logger.info("Command received: grasp - Setting objective angle to 3.14")
        elif command == "release":
            self.objective_angle = 0.2
            self.active_command = "release"
            self.alpha = self.alpha_release
            self.beta = self.beta_release
            logger.info("Command received: release - Setting objective angle to 0.0")
        elif command == "stop":
            self.previous_intensity = 0
            self.intensity = 0
            self.error = 0
            self.objective_angle = None
            stim_code = [0, 0, 0, 0, 0, 0, 0, 0]
            self.stim.UpdateChannelSettings(stim_code)
            time.sleep(5)
        elif command == "pinch":
            self.objective_angle = 1.57
            self.active_command = "pinch"
            logger.info("Command received: pinch - Setting objective angle to 1.57")
        elif command == "calibration":
            self.active_command = "calibration"
            logger.info("Calibration")

    def update_sensor_reading(self, angle, timestamp):

        # Only stimulate if we have an active command
        if self.active_command:
            if self.active_command not in ["calibration", "stop"]:
                if timestamp - self.previous_angle_timestamp < 500:
                    # Ignore readings that are too close together
                    return

                self.previous_angle_timestamp = timestamp
                self.current_angle = angle

                self.intensity = self.calculate_stimulation_intensity()
                self.stimulate(self.intensity, self.active_command)
            elif self.active_command == "calibration":
                if (
                    timestamp - self.previous_angle_timestamp < 2500
                    or self.intensity_idx >= len(self.calibration_intensities) - 1
                ):
                    # Ignore readings that are too close together
                    return
                with open("calibration_set.txt", "a") as f:
                    f.write(
                        f"{self.calibration_intensities[self.intensity_idx]} {angle} \n"
                    )

                self.previous_angle_timestamp = timestamp
                self.intensity_idx += 1
                self.stimulate(
                    self.calibration_intensities[self.intensity_idx],
                    self.active_command,
                )


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
        # if not stimulator.is_rec:
        #     stimulator.process_command("grasp")
        #     stimulator.is_rec = True

        try:
            payload = json.loads(msg.payload.decode())
            print(f"Received message on topic {msg.topic}: {payload}")

            if msg.topic == "/sensor":
                if "grasp_angle" in payload:
                    stimulator.update_sensor_reading(
                        payload["grasp_angle"], payload["timestamp_ms"]
                    )
                    if stimulator.active_command == "calibration":
                        with open("calibration.txt", "a") as f:
                            f.write(
                                f"{stimulator.calibration_intensities[stimulator.intensity_idx]} {payload['grasp_angle']}\n"
                            )
                    else:
                        with open("experiment_GR_7.txt", "a") as f:
                            f.write(
                                f"{stimulator.intensity} {payload['grasp_angle']} {stimulator.error}\n"
                            )

            elif msg.topic == "/command":
                if "action" in payload:
                    stimulator.process_command(payload["action"])

        except json.JSONDecodeError:
            print(f"Error decoding JSON from message: {msg.payload.decode()}")
        except Exception as e:
            print(f"Error processing message: {e}")

    client = mqtt.Client()
    mqtt_hostname = os.getenv("MQTT_HOSTNAME")
    if mqtt_hostname is None:
        mqtt_hostname = "localhost"
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(mqtt_hostname, 1883, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("Stimulator stopped by user")
    finally:
        # Ensure stimulator is properly closed
        del stimulator


if __name__ == "__main__":
    main()
