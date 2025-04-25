// SpeechRecognitionViewModel.kt
package ch.heigvd.iict.daa.template


import android.speech.SpeechRecognizer
import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel


class SpeechRecognitionViewModel : ViewModel() {

    private val _recognitionStatus = MutableLiveData<String>()
    val recognitionStatus: LiveData<String> = _recognitionStatus

    private val _graspDetected = MutableLiveData<Boolean>()
    val graspDetected: LiveData<Boolean> = _graspDetected

    private val targetWord = "grasp"
    // Add similar-sounding words that might be detected instead
    private val similarSoundingWords = listOf("grasp", "grass", "grasse", "rasp", "grasp", "gasp", "grâce")

    init {
        _recognitionStatus.value = "Ready to listen"
        _graspDetected.value = false
    }

    fun updateStatus(status: String) {
        _recognitionStatus.value = status
        Log.d(TAG, "Status updated: $status")
    }

    fun handleError(error: Int) {
        val errorMessage = when (error) {
            SpeechRecognizer.ERROR_AUDIO -> "Audio recording error"
            SpeechRecognizer.ERROR_CLIENT -> "Client side error"
            SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Insufficient permissions"
            SpeechRecognizer.ERROR_NETWORK -> "Network error"
            SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Network timeout"
            SpeechRecognizer.ERROR_NO_MATCH -> "No match found"
            SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "RecognitionService busy"
            SpeechRecognizer.ERROR_SERVER -> "Server error"
            SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "No speech input"
            else -> "Unknown error"
        }

        _recognitionStatus.value = "Error: $errorMessage"
        Log.e(TAG, "Speech recognition error: $errorMessage")
    }

    fun processResults(results: ArrayList<String>) {
        if (results.isNotEmpty()) {
            val recognizedText = results[0].lowercase()
            Log.d(TAG, "Recognized: $recognizedText")

            // Log all alternatives for debugging
            for (i in 0 until results.size) {
                Log.d(TAG, "Alternative $i: ${results[i]}")
            }

            _recognitionStatus.value = "Recognized: $recognizedText"

            checkForTargetWord(recognizedText)

            // Check all alternatives if main recognition didn't match
            if (!_graspDetected.value!!) {
                for (i in 1 until results.size) {
                    checkForTargetWord(results[i].lowercase())
                    if (_graspDetected.value!!) {
                        _recognitionStatus.value = "Detected in alternative: ${results[i]}"
                        break
                    }
                }
            }
        }
    }

    fun processPartialResults(partialResults: ArrayList<String>) {
        if (partialResults.isNotEmpty()) {
            val recognizedText = partialResults[0].lowercase()
            _recognitionStatus.value = "Partial: $recognizedText"

            // Log all alternatives for debugging
            for (i in 0 until partialResults.size) {
                Log.d(TAG, "Partial Alt $i: ${partialResults[i]}")
            }

            checkForTargetWord(recognizedText)
        }
    }

    private fun checkForTargetWord(text: String) {
        // First check for exact match
        if (text.contains(targetWord)) {
            Log.d(TAG, "TARGET WORD '$targetWord' DETECTED!")
            _graspDetected.value = true
            //Send request to MTT Server
            return
        }

        // Check for similar sounding words
        for (word in similarSoundingWords) {
            if (text.contains(word)) {
                Log.d(TAG, "Similar word '$word' detected, treating as '$targetWord'")
                _graspDetected.value = true
                return
            }
        }

        // Check for distance-based similarity (Levenshtein distance)
        val words = text.split(" ")
        for (word in words) {
            if (word.length >= 3 && calculateLevenshteinDistance(word, targetWord) <= 2) {
                Log.d(TAG, "Similar word '$word' detected with Levenshtein distance <= 2, treating as '$targetWord'")
                _graspDetected.value = true
                return
            }
        }
    }

    // Calculate Levenshtein distance between two strings
    private fun calculateLevenshteinDistance(s1: String, s2: String): Int {
        val costs = IntArray(s2.length + 1)
        for (i in 0..s2.length) {
            costs[i] = i
        }

        for (i in 1..s1.length) {
            var lastValue = i
            for (j in 1..s2.length) {
                val oldValue = costs[j]
                costs[j] = minOf(
                    costs[j] + 1,
                    costs[j - 1] + 1,
                    lastValue + if (s1[i - 1] == s2[j - 1]) 0 else 1
                )
                lastValue = oldValue
            }
        }

        return costs[s2.length]
    }

    fun resetGraspDetection() {
        _graspDetected.value = false
    }

    companion object {
        private const val TAG = "SpeechRecVM"
    }
}
