// MqttClientService.kt
package ch.heigvd.iict.daa.template


import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Binder
import android.os.IBinder
import android.util.Log
import org.eclipse.paho.client.mqttv3.*
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import java.util.*

class MqttClientService : Service() {

    companion object {
        private const val TAG = "MqttClientService"
        private const val DEFAULT_QOS = 1
        private const val DEFAULT_RETAINED = false
    }

    private val binder = LocalBinder()
    private var mqttClient: MqttClient? = null
    private var serverUri: String? = null
    private var clientId: String = "AndroidClient-" + UUID.randomUUID().toString()

    inner class LocalBinder : Binder() {
        fun getService(): MqttClientService = this@MqttClientService
    }

    override fun onBind(intent: Intent): IBinder {
        return binder
    }

    override fun onDestroy() {
        disconnect()
        super.onDestroy()
    }

    /**
     * Connect to an MQTT broker
     * @param serverUri The broker URL, typically in the format: "tcp://broker.example.com:1883" or "ssl://broker.example.com:8883"
     * @param username Optional username for authentication
     * @param password Optional password for authentication
     * @param callback Callback to notify about connection status
     */
    fun connect(
        serverUri: String,
        username: String? = null,
        password: String? = null,
        callback: IMqttActionListener? = null
    ) {
        try {
            this.serverUri = serverUri

            // Setup MQTT client
            val persistence = MemoryPersistence()
            mqttClient = MqttClient(serverUri, clientId, persistence)

            val options = MqttConnectOptions().apply {
                isCleanSession = true
                connectionTimeout = 30
                keepAliveInterval = 60

                // Set credentials if provided
                if (!username.isNullOrEmpty() && !password.isNullOrEmpty()) {
                    this.userName = username
                    this.password = password.toCharArray()
                }
            }

            // Set callbacks for connection events
            mqttClient?.setCallback(object : MqttCallback {
                override fun connectionLost(cause: Throwable?) {
                    Log.e(TAG, "Connection lost", cause)
                }

                override fun messageArrived(topic: String?, message: MqttMessage?) {
                    Log.d(TAG, "Message received: ${message?.toString() ?: "null"}, topic: $topic")
                }

                override fun deliveryComplete(token: IMqttDeliveryToken?) {
                    Log.d(TAG, "Message delivered")
                }
            })

            // Connect to the broker
            mqttClient?.connectWithResult(options)?.let {
                Log.d(TAG, "Connected to broker: $serverUri")
                callback?.onSuccess(it)
            }
        } catch (e: MqttException) {
            Log.e(TAG, "Error connecting to MQTT broker", e)
            callback?.onFailure(null, e)
        }
    }

    /**
     * Publish a message to a topic
     * @param topic The topic to publish to
     * @param message The message payload
     * @param qos Quality of Service (0, 1, or 2)
     * @param retained Whether the broker should retain the message
     * @param callback Callback to notify about publish status
     */
    fun publish(
        topic: String,
        message: String,
        qos: Int = DEFAULT_QOS,
        retained: Boolean = DEFAULT_RETAINED,
        callback: IMqttActionListener? = null
    ) {
        if (mqttClient == null || !mqttClient!!.isConnected) {
            Log.e(TAG, "Cannot publish: not connected to broker")
            callback?.onFailure(null, MqttException(32104))
            return
        }

        try {
            val mqttMessage = MqttMessage().apply {
                payload = message.toByteArray()
                this.qos = qos
                this.isRetained = retained
            }

            mqttClient?.publish(topic, mqttMessage.payload, mqttMessage.qos, mqttMessage.isRetained)
            Log.d(TAG, "Published message: '$message' to topic: '$topic'")
        } catch (e: MqttException) {
            Log.e(TAG, "Error publishing message", e)
            callback?.onFailure(null, e)
        }
    }

    /**
     * Disconnect from the MQTT broker
     */
    fun disconnect() {
        try {
            mqttClient?.disconnect()
            Log.d(TAG, "Disconnected from broker")
        } catch (e: MqttException) {
            Log.e(TAG, "Error disconnecting from broker", e)
        } finally {
            mqttClient = null
        }
    }

    /**
     * Check if client is connected to the broker
     * @return true if connected, false otherwise
     */
    fun isConnected(): Boolean {
        return mqttClient?.isConnected ?: false
    }
}
