package ch.heigvd.iict.daa.template

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.ProgressBar
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.net.URL

const val CACHE_AGE = 5 * 60 * 1000 // 5 minutes

class RecycleViewAdapter(
    private val lifecycleOwner: LifecycleOwner,
    _id_images: List<Int> = listOf()
) : RecyclerView.Adapter<RecycleViewAdapter.ViewHolder>() {

    var id_images = listOf<Int>()
        set(value) {
            field = value
        }

    init {
        id_images = _id_images
    }

    companion object {
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        return ViewHolder(LayoutInflater.from(parent.context).inflate(R.layout.image, parent, false), lifecycleOwner)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(id_images[position])
    }

    override fun getItemCount(): Int {
        return id_images.size
    }

    inner class ViewHolder(view: View, private val lifecycleOwner: LifecycleOwner) : RecyclerView.ViewHolder(view) {
        private val image = view.findViewById<ImageView>(R.id.image)
        private val progessBar = view.findViewById<ProgressBar>(R.id.progessBar)
        private val cacheRoot: File = view.context.cacheDir
        private var job: kotlinx.coroutines.Job? = null;

        fun bind(image_id: Int) {
            image.contentDescription = image_id.toString()
            image.visibility = View.GONE
            progessBar.visibility = View.VISIBLE
            fetchImage(image_id);
        }

        private suspend fun loadFromCache(id: Int): ByteArray? = withContext(Dispatchers.IO) {
            val fileName = "$id.jpg"
            val file = File(cacheRoot, fileName)
            if (file.exists()) {
                val fileAge = (System.currentTimeMillis() - file.lastModified()) / 1000 * 60;
                if (fileAge < CACHE_AGE) {
                    try {
                        file.readBytes()
                    } catch (e: IOException) {
                        Log.w("loadFromCache", "Exception while downloading image", e)
                        null
                    }
                } else {
                    Log.w("loadFromCache", "Image in cache expired")
                    file.delete();
                    null
                }
            } else {
                null
            }
        }

        private suspend fun saveToCache(id: Int, bytes: ByteArray?) = withContext(Dispatchers.IO) {
            val fileName = "$id.jpg"
            val file = File(cacheRoot, fileName)
            try {
                FileOutputStream(file).use { outputStream ->
                    outputStream.write(bytes)
                }
            } catch (e: IOException) {
                Log.w("saveToCache", "Failed to save image to cache")
            }
        }

        private suspend fun downloadImage(url: URL): ByteArray? = withContext(Dispatchers.IO) {
            try {
                url.readBytes()
            } catch (e: IOException) {
                Log.w("downloadImage", "Exception while downloading image", e)
                null
            }
        }


        private suspend fun decodeImage(bytes: ByteArray?): Bitmap? = withContext(Dispatchers.Default) {
            try {
                BitmapFactory.decodeByteArray(bytes, 0, bytes?.size ?: 0)
            } catch (e: IOException) {
                Log.w("decodeImage", "Exception while decoding image", e)
                null
            }
        }

        private suspend fun displayImage(bitmap: Bitmap?) = withContext(Dispatchers.Main) {
            image.setImageBitmap(bitmap)
            image.visibility = View.VISIBLE
            progessBar.visibility = View.GONE
        }

        fun fetchImage(id: Int) {
            job = lifecycleOwner.lifecycleScope.launch {
                var bytes = loadFromCache(id);
                if (bytes == null) {
                    val url = URL("https://daa.iict.ch/images/$id.jpg")
                    bytes = downloadImage(url)
                    saveToCache(id, bytes)
                }
                val bmp = decodeImage(bytes)
                displayImage(bmp)
            }
        }

        fun stopCorutine() {
            job?.cancel()
        }
    }

    override fun onViewRecycled(holder: ViewHolder) {
        super.onViewRecycled(holder)
        holder.stopCorutine()
    }
}