import paho.mqtt.client as mqtt
import time
import math

client = mqtt.Client()
client.connect("cluster.jolivier.ch", 1883, 60)

# Give some time to establish connection
angle = 0.0
step = 0.1  # Step size for angle increment

while True:
    time.sleep(1)

    msg = f"{{\"timestamp_ms\": {int(time.time() * 1000)}, \"grasp_angle\": {angle}}}"
    client.publish("/sensor", msg)
    print(f"Published msg: {msg}")

    # Update angle
    angle += step
    if angle >= math.pi or angle <= 0:
        break
        # step = -step  # Reverse direction when reaching bounds
client.disconnect()
