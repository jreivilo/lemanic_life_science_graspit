package ch.heigvd.iict.daa.template

import android.content.Context
import androidx.work.Worker
import androidx.work.WorkerParameters
import java.io.File
import java.nio.file.Files.delete

class MyWorker(context: Context, workerParams: WorkerParameters) : Worker(context, workerParams) {

    override fun doWork(): Result {
        try {
            println("Running background task...")

            Thread.sleep(2000)

            return Result.success()  // Task succeeded
        } catch (e: Exception) {
            return Result.failure()  // Task failed
        }
    }


    fun deleteCache(cacheDir : File) {
        try {
            for (file in cacheDir.list()!!) {


            }

        } catch (e: Exception) {
            e.printStackTrace();
        }
    }
}
