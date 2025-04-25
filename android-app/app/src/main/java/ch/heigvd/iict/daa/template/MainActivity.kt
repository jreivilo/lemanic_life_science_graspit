package ch.heigvd.iict.daa.template

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Start the MQTT service
        startService(Intent(this, MqttClientService::class.java))

        // Only add the fragment if this is the first creation
        if (savedInstanceState == null) {
            // Launch the speech recognition fragment
            supportFragmentManager.beginTransaction()
                .replace(R.id.fragment_container, SpeechRecognitionFragment())
                .commit()
        }
    }


    override fun onDestroy() {
        super.onDestroy()

        // Stop the MQTT service when the activity is destroyed
        // Note: You might want to keep it running if you need background MQTT functionality
        stopService(Intent(this, MqttClientService::class.java))
    }
}