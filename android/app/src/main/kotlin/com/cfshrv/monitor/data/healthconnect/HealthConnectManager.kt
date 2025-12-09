package com.cfshrv.monitor.data.healthconnect

import android.content.Context
import android.util.Log
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.HeartRateVariabilityRmssdRecord
import androidx.health.connect.client.records.SleepSessionRecord
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import com.cfshrv.monitor.data.model.HrvData
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.time.Instant
import java.time.ZonedDateTime
import java.time.temporal.ChronoUnit

/**
 * Manager for Health Connect integration.
 * Handles permissions and data retrieval from Health Connect.
 */
class HealthConnectManager(private val context: Context) {

    companion object {
        private const val TAG = "HealthConnectManager"

        // Required permissions
        val PERMISSIONS = setOf(
            HealthPermission.getReadPermission(HeartRateVariabilityRmssdRecord::class),
            HealthPermission.getReadPermission(HeartRateRecord::class),
            HealthPermission.getReadPermission(SleepSessionRecord::class)
        )
    }

    private val healthConnectClient by lazy {
        HealthConnectClient.getOrCreate(context)
    }

    /**
     * Check if Health Connect is available on this device
     */
    suspend fun isAvailable(): Boolean {
        return HealthConnectClient.getSdkStatus(context) == HealthConnectClient.SDK_AVAILABLE
    }

    /**
     * Check if we have all required permissions
     */
    suspend fun hasAllPermissions(): Boolean {
        val granted = healthConnectClient.permissionController.getGrantedPermissions()
        return granted.containsAll(PERMISSIONS)
    }

    /**
     * Get HRV data for the last 24 hours
     */
    suspend fun getLatestHrvData(): HrvData? {
        return try {
            val endTime = Instant.now()
            val startTime = endTime.minus(24, ChronoUnit.HOURS)

            // Read HRV RMSSD records
            val hrvResponse = healthConnectClient.readRecords(
                ReadRecordsRequest(
                    recordType = HeartRateVariabilityRmssdRecord::class,
                    timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
                )
            )

            val hrvRecord = hrvResponse.records.lastOrNull()
            if (hrvRecord == null) {
                Log.w(TAG, "No HRV data found in last 24 hours")
                return null
            }

            // Read heart rate for the same period
            val hrResponse = healthConnectClient.readRecords(
                ReadRecordsRequest(
                    recordType = HeartRateRecord::class,
                    timeRangeFilter = TimeRangeFilter.between(
                        hrvRecord.time.minus(1, ChronoUnit.HOURS),
                        hrvRecord.time.plus(1, ChronoUnit.HOURS)
                    )
                )
            )

            val avgHeartRate = hrResponse.records
                .flatMap { it.samples }
                .map { it.beatsPerMinute }
                .average()

            // Read sleep data
            val sleepResponse = healthConnectClient.readRecords(
                ReadRecordsRequest(
                    recordType = SleepSessionRecord::class,
                    timeRangeFilter = TimeRangeFilter.between(
                        hrvRecord.time.minus(12, ChronoUnit.HOURS),
                        hrvRecord.time.plus(12, ChronoUnit.HOURS)
                    )
                )
            )

            val sleepSession = sleepResponse.records.lastOrNull()
            val sleepDurationHours = sleepSession?.let {
                ChronoUnit.MINUTES.between(it.startTime, it.endTime) / 60.0
            }

            HrvData(
                timestamp = hrvRecord.time,
                rmssdMs = hrvRecord.heartRateVariabilityMillis,
                heartRateBpm = avgHeartRate,
                sleepDurationHours = sleepDurationHours,
                sleepQualityScore = null // Health Connect doesn't provide sleep quality score
            )

        } catch (e: Exception) {
            Log.e(TAG, "Error reading HRV data from Health Connect", e)
            null
        }
    }

    /**
     * Get HRV data for a specific date range
     */
    suspend fun getHrvDataInRange(
        startTime: Instant,
        endTime: Instant
    ): List<HrvData> {
        return try {
            val hrvResponse = healthConnectClient.readRecords(
                ReadRecordsRequest(
                    recordType = HeartRateVariabilityRmssdRecord::class,
                    timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
                )
            )

            hrvResponse.records.mapNotNull { hrvRecord ->
                try {
                    // Get heart rate around the same time
                    val hrResponse = healthConnectClient.readRecords(
                        ReadRecordsRequest(
                            recordType = HeartRateRecord::class,
                            timeRangeFilter = TimeRangeFilter.between(
                                hrvRecord.time.minus(1, ChronoUnit.HOURS),
                                hrvRecord.time.plus(1, ChronoUnit.HOURS)
                            )
                        )
                    )

                    val avgHeartRate = hrResponse.records
                        .flatMap { it.samples }
                        .map { it.beatsPerMinute }
                        .average()

                    HrvData(
                        timestamp = hrvRecord.time,
                        rmssdMs = hrvRecord.heartRateVariabilityMillis,
                        heartRateBpm = avgHeartRate,
                        sleepDurationHours = null,
                        sleepQualityScore = null
                    )
                } catch (e: Exception) {
                    Log.w(TAG, "Error processing HRV record", e)
                    null
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error reading HRV data range from Health Connect", e)
            emptyList()
        }
    }

    /**
     * Continuously monitor for new HRV data
     */
    fun observeHrvData(): Flow<HrvData?> = flow {
        while (true) {
            val data = getLatestHrvData()
            emit(data)
            kotlinx.coroutines.delay(60_000) // Check every minute
        }
    }
}
