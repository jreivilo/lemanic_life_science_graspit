// SpeechRecognitionFragment.kt
package ch.heigvd.iict.daa.template

import android.Manifest
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.IBinder
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import org.eclipse.paho.client.mqttv3.IMqttActionListener
import org.eclipse.paho.client.mqttv3.IMqttToken

class SpeechRecognitionFragment : Fragment() {

    // MQTT service properties
    private var mqttService: MqttClientService? = null
    private var bound: Boolean = false
    private val brokerUrl = "tcp://cluster.jolivier.ch:1883"
    private val topic = "/command"

    // Speech recognition parameters
    private lateinit var viewModel: SpeechRecognitionViewModel
    private lateinit var speechRecognizer: SpeechRecognizer
    private lateinit var recordButton: Button
    private lateinit var statusTextView: TextView
    private lateinit var detectionInfoTextView: TextView

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            Log.d(TAG, "Permission granted")
        } else {
            Toast.makeText(
                requireContext(),
                "Audio recording permission is required for speech recognition",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    // Service connection for MQTT
    private val connection = object : ServiceConnection {
        override fun onServiceConnected(className: ComponentName, service: IBinder) {
            val binder = service as MqttClientService.LocalBinder
            mqttService = binder.getService()
            bound = true
            Log.d(TAG, "MQTT Service connected")

            // Try to connect to broker once service is bound
            connectToMqttBroker()
        }

        override fun onServiceDisconnected(arg0: ComponentName) {
            bound = false
            mqttService = null
            Log.d(TAG, "MQTT Service disconnected")
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = ViewModelProvider(this)[SpeechRecognitionViewModel::class.java]
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_speech_recognition, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        recordButton = view.findViewById(R.id.recordButton)
        statusTextView = view.findViewById(R.id.statusTextView)
        detectionInfoTextView = view.findViewById(R.id.detectionInfoTextView)

        // Initialize speech recognizer
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(requireContext())
        speechRecognizer.setRecognitionListener(createRecognitionListener())

        // Set up record button
        recordButton.setOnClickListener {
            checkPermissionAndStartListening()
        }

        // Observe recognition status
        viewModel.recognitionStatus.observe(viewLifecycleOwner) { status ->
            statusTextView.text = status
        }

        // Observe when "grasp" is detected
        viewModel.graspDetected.observe(viewLifecycleOwner) { detected ->
            if (detected) {
                statusTextView.text = "Word 'grasp' detected!"
                detectionInfoTextView.apply {
                    text = "GRASP DETECTED!"

                    // TODO -  Send message as json

                    publishMessage("Hello from existing fragment!")
                    setTextColor(resources.getColor(android.R.color.holo_green_dark, null))
                }
                // Make the text flash by changing its visibility
                view.post {
                    val flashAnimation = object : Runnable {
                        var count = 0
                        override fun run() {
                            if (count < 6) { // Flash 3 times (on/off cycles)
                                detectionInfoTextView.visibility =
                                    if (detectionInfoTextView.visibility == View.VISIBLE)
                                        View.INVISIBLE else View.VISIBLE
                                count++
                                view.postDelayed(this, 300) // Toggle every 300ms
                            } else {
                                detectionInfoTextView.visibility = View.VISIBLE
                                viewModel.resetGraspDetection()
                            }
                        }
                    }
                    view.post(flashAnimation)
                }
            }
        }
    }

    override fun onStart() {
        super.onStart()
        // Bind to the MQTT service when fragment starts
        Intent(requireContext(), MqttClientService::class.java).also { intent ->
            requireActivity().bindService(intent, connection, Context.BIND_AUTO_CREATE)
        }
    }

    override fun onStop() {
        super.onStop()
        // Unbind from the service when fragment stops
        if (bound) {
            requireActivity().unbindService(connection)
            bound = false
        }
    }

    // MQTT functions

    private fun connectToMqttBroker() {
        if (!bound || mqttService == null) {
            showToast("MQTT Service not bound")
            return
        }

        mqttService?.connect(
            serverUri = brokerUrl,
            callback = object : IMqttActionListener {
                override fun onSuccess(asyncActionToken: IMqttToken?) {
                    requireActivity().runOnUiThread {
                        showToast("Connected to MQTT broker")
                    }
                }

                override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                    requireActivity().runOnUiThread {
                        showToast("Failed to connect: ${exception?.message}")
                    }
                }
            }
        )
    }

    private fun publishMessage(message: String) {
        if (!bound || mqttService == null) {
            showToast("MQTT Service not bound")
            return
        }

        if (!mqttService!!.isConnected()) {
            showToast("Not connected to MQTT broker")
            return
        }


        mqttService?.publish(
            topic = topic,
            message = message,
            callback = object : IMqttActionListener {
                override fun onSuccess(asyncActionToken: IMqttToken?) {
                    requireActivity().runOnUiThread {
                        showToast("Message published successfully")
                    }
                }

                override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                    requireActivity().runOnUiThread {
                        showToast("Failed to publish message: ${exception?.message}")
                    }
                }
            }
        )
    }
    private fun showToast(message: String) {
        Toast.makeText(requireContext(), message, Toast.LENGTH_SHORT).show()
        Log.d(TAG, message)
    }
    private fun createRecognitionListener(): RecognitionListener {
        return object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                viewModel.updateStatus("Listening...")
            }

            override fun onBeginningOfSpeech() {
                viewModel.updateStatus("Started listening")
            }

            override fun onRmsChanged(rmsdB: Float) {
                // Not used, but required to implement
            }

            override fun onBufferReceived(buffer: ByteArray?) {
                // Not used, but required to implement
            }

            override fun onEndOfSpeech() {
                viewModel.updateStatus("Stopped listening")
            }

            override fun onError(error: Int) {
                viewModel.handleError(error)
            }

            override fun onResults(results: Bundle?) {
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                matches?.let {
                    viewModel.processResults(it)
                }
            }

            override fun onPartialResults(partialResults: Bundle?) {
                val matches = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                matches?.let {
                    viewModel.processPartialResults(it)
                }
            }

            override fun onEvent(eventType: Int, params: Bundle?) {
                // Not used, but required to implement
            }
        }
    }

    private fun checkPermissionAndStartListening() {
        when {
            ContextCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.RECORD_AUDIO
            ) == PackageManager.PERMISSION_GRANTED -> {
                startListening()
            }
            shouldShowRequestPermissionRationale(Manifest.permission.RECORD_AUDIO) -> {
                Toast.makeText(
                    requireContext(),
                    "Audio recording permission is required for speech recognition",
                    Toast.LENGTH_LONG
                ).show()
                requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
            }
            else -> {
                requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
            }
        }
    }

    private fun startListening() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, requireActivity().packageName)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)

            // Request maximum results
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 10)

            // Add these extras to improve recognition accuracy
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS, 1000)
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 1000)
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, 1000)

            // Add preferred phrases - this can help bias the recognizer
            val phrases = arrayListOf("grasp", "grasp the object", "try to grasp")
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true) // Use offline recognition if available
        }

        try {
            speechRecognizer.startListening(intent)
            Log.d(TAG, "Started listening with enhanced settings")
        } catch (e: Exception) {
            Log.e(TAG, "Error starting speech recognition: ${e.message}")
            Toast.makeText(requireContext(), "Could not start speech recognition", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        speechRecognizer.destroy()
    }

    companion object {
        private const val TAG = "SpeechRecFragment"
    }
}