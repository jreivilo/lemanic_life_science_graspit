import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.connect("cluster.jolivier.ch", 1883, 60)

# Give some time to establish connection
while True:
    time.sleep(1)

    client.publish("test/topic", "Hello from publisher!")
    print("Message published.")

client.disconnect()
