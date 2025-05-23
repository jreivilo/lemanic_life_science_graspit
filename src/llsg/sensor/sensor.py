import json
import time
from dataclasses import asdict
import os
import leap
import numpy as np
import paho.mqtt.client as mqtt

from llsg.data_structure import HandPose

client = mqtt.Client()
mqtt_hostname = os.getenv("MQTT_HOSTNAME")
if mqtt_hostname is None:
    mqtt_hostname = "localhost"

def quaternion_conjugate(q):
    """Returns the conjugate of a quaternion."""
    w, x, y, z = q
    return np.array([w, -x, -y, -z])


def quaternion_multiply(q1, q2):
    """Multiplies two quaternions."""
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array(
        [
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        ]
    )


def quaternion_difference(q1, q2):
    """
    Returns the relative rotation (difference) quaternion q_diff such that:
    q2 = q_diff * q1
    So: q_diff = q2 * conjugate(q1)
    """
    q1_conj = quaternion_conjugate(q1)
    return quaternion_multiply(q2, q1_conj)


# hand = Hand object from the Leap API
def send_data(hand):
    handPose = HandPose(timestamp_ms=0, grasp_angle=0.0)
    handPose.timestamp_ms = int(time.time() * 1000)
    handPose.grasp_angle = hand.grab_angle

    # # Add orientation of the wrist
    # q1 = hand.palm.orientation
    # q2 = hand.arm.rotation
    # qdiff = quaternion_difference(q1, q2)
    # handPose["wrist_orientation"] = qdiff
    #
    # handPose["digits"] = []
    # # Iterate every fingers
    # for i in range(len(hand.digits)):
    #     print(f"digit {i}")
    #     handPose["digits"].append([])
    #
    #     # Iterate every bones of the finger
    #     for j in range(len(hand.digits[i].bones) - 1):
    #         print(f"joint {j}")
    #         q1 = hand.digits[i].bones[j].rotation
    #         q2 = hand.digits[i].bones[j + 1].rotation
    #         qdiff = quaternion_difference(q1, q2)

    #         # Maybe only get a euler angle instead of 4 values of the quaternion ?
    #         handPose["digits"][i].append(qdiff)

    # Send data to the server
    client.publish("/sensor", json.dumps(asdict(handPose)))
    print(handPose)


class MyListener(leap.Listener):
    def on_connection_event(self, event):
        print("Connected")
        self.prev = time.time()

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")

    def on_tracking_event(self, event):
        if time.time() - self.prev < 0.1:
            return
        self.prev = time.time()
        for hand in event.hands:
            send_data(hand)


def main():
    # Init connection to MQTT server
    client.connect(mqtt_hostname, 1883, 60)

    my_listener = MyListener()

    connection = leap.Connection()
    connection.add_listener(my_listener)

    running = True

    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)
        while running:
            time.sleep(1)

    client.disconnect()


if __name__ == "__main__":
    main()
