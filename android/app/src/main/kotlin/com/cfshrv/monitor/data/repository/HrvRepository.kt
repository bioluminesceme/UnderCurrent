package com.cfshrv.monitor.data.repository

import android.content.Context
import android.util.Log
import com.cfshrv.monitor.data.api.CfsHrvApiClient
import com.cfshrv.monitor.data.healthconnect.HealthConnectManager
import com.cfshrv.monitor.data.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.time.Instant
import java.time.format.DateTimeFormatter

/**
 * Repository that coordinates Health Connect data with the backend API.
 * This is the main data layer for the app.
 */
class HrvRepository(
    context: Context,
    private val apiClient: CfsHrvApiClient = CfsHrvApiClient()
) {
    companion object {
        private const val TAG = "HrvRepository"
    }

    private val healthConnectManager = HealthConnectManager(context)

    /**
     * Check if Health Connect is available and has permissions
     */
    suspend fun isHealthConnectReady(): Boolean {
        return healthConnectManager.isAvailable() && healthConnectManager.hasAllPermissions()
    }

    /**
     * Get latest HRV data from Health Connect
     */
    suspend fun getLatestHrvData(): HrvData? {
        return healthConnectManager.getLatestHrvData()
    }

    /**
     * Sync with synthetic demo data (for testing without Health Connect)
     */
    suspend fun syncWithDemoData(userId: Int): Result<EnergyBudgetResponse> {
        return try {
            Log.d(TAG, "Syncing with demo data...")

            // Generate realistic demo RR intervals
            val syntheticRRIntervals = generateSyntheticRRIntervals(
                meanHr = 65.0,  // 65 bpm resting heart rate
                rmssd = 45.0,   // 45ms RMSSD (healthy range)
                count = 300
            )

            // Submit to backend
            val request = RRIntervalsRequest(
                rrIntervals = syntheticRRIntervals,
                recordedAt = java.time.Instant.now().toString(),
                sleepDuration = 7.5,  // 7.5 hours of sleep
                sleepQuality = 85.0   // 85% sleep quality
            )

            Log.d(TAG, "Submitting demo HRV reading...")
            val readingResult = apiClient.submitHrvReading(userId, request)
            if (readingResult.isFailure) {
                Log.e(TAG, "Failed to submit reading", readingResult.exceptionOrNull())
                return Result.failure(readingResult.exceptionOrNull()!!)
            }

            val reading = readingResult.getOrThrow()
            Log.d(TAG, "Reading submitted with ID: ${reading.id}")

            // Calculate energy budget
            Log.d(TAG, "Calculating energy budget...")
            val result = apiClient.calculateEnergyBudget(userId, reading.id)
            Log.d(TAG, "Energy budget result: ${result.isSuccess}")
            result

        } catch (e: Exception) {
            Log.e(TAG, "Error syncing demo data to backend", e)
            Result.failure(e)
        }
    }

    /**
     * Sync latest HRV data from Health Connect to backend
     *
     * Note: This is a simplified version that uses RMSSD directly.
     * For full frequency domain analysis, you would need raw RR intervals.
     */
    suspend fun syncLatestHrvToBackend(userId: Int): Result<EnergyBudgetResponse> {
        return try {
            Log.d(TAG, "Attempting to get HRV data from Health Connect...")

            // Try to get latest HRV data from Health Connect
            // This will fail if we don't have permissions, which is fine
            val hrvData = try {
                healthConnectManager.getLatestHrvData()
            } catch (e: SecurityException) {
                Log.e(TAG, "Security exception - no Health Connect permissions", e)
                return Result.failure(Exception("No Health Connect permissions. Please grant permissions in Settings → Apps → Health Connect → App permissions → CFS-HRV Monitor"))
            } catch (e: Exception) {
                Log.e(TAG, "Error reading from Health Connect", e)
                return Result.failure(Exception("Error reading Health Connect: ${e.message}"))
            }

            if (hrvData == null) {
                return Result.failure(Exception("No HRV data available from Health Connect. Make sure your Garmin watch has synced recently."))
            }

            Log.d(TAG, "Got HRV data: RMSSD=${hrvData.rmssdMs}ms, HR=${hrvData.heartRateBpm}bpm")

            // For now, we'll create synthetic RR intervals from RMSSD
            // In a real implementation, you'd need actual RR intervals from the device
            val syntheticRRIntervals = generateSyntheticRRIntervals(
                meanHr = hrvData.heartRateBpm,
                rmssd = hrvData.rmssdMs,
                count = 300
            )

            // Submit to backend
            val request = RRIntervalsRequest(
                rrIntervals = syntheticRRIntervals,
                recordedAt = hrvData.timestamp.toString(),
                sleepDuration = hrvData.sleepDurationHours,
                sleepQuality = hrvData.sleepQualityScore
            )

            Log.d(TAG, "Submitting HRV reading to backend...")
            val readingResult = apiClient.submitHrvReading(userId, request)
            if (readingResult.isFailure) {
                return Result.failure(readingResult.exceptionOrNull()!!)
            }

            val reading = readingResult.getOrThrow()
            Log.d(TAG, "Reading submitted with ID: ${reading.id}")

            // Calculate readiness score
            Log.d(TAG, "Calculating energy budget...")
            apiClient.calculateEnergyBudget(userId, reading.id)

        } catch (e: Exception) {
            Log.e(TAG, "Error syncing HRV data to backend", e)
            Result.failure(e)
        }
    }

    /**
     * Get current readiness score
     */
    suspend fun getCurrentEnergyBudget(userId: Int): Result<EnergyBudgetResponse> {
        return try {
            val scores = apiClient.getEnergyBudgets(userId, limit = 1)
            if (scores.isSuccess && scores.getOrNull()?.isNotEmpty() == true) {
                Result.success(scores.getOrThrow().first())
            } else {
                Result.failure(Exception("No readiness scores available"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get readiness trend
     */
    suspend fun getEnergyBudgetTrend(userId: Int, days: Int = 7): Result<List<Map<String, Any>>> {
        return apiClient.getEnergyBudgetTrend(userId, days)
    }

    /**
     * Calculate baseline (requires at least 7 days of data)
     */
    suspend fun calculateBaseline(userId: Int): Result<BaselineResponse> {
        return apiClient.calculateBaseline(userId)
    }

    /**
     * Get active baseline
     */
    suspend fun getActiveBaseline(userId: Int): Result<BaselineResponse> {
        return apiClient.getActiveBaseline(userId)
    }

    /**
     * Create a new user
     */
    suspend fun createUser(request: UserCreateRequest): Result<UserResponse> {
        return apiClient.createUser(request)
    }

    /**
     * Generate synthetic RR intervals from RMSSD and mean HR
     *
     * This is a workaround since Health Connect provides RMSSD but not raw RR intervals.
     * For production, you should:
     * 1. Use actual RR intervals if your device provides them
     * 2. Or just use RMSSD directly (modify backend to accept it)
     */
    private fun generateSyntheticRRIntervals(
        meanHr: Double,
        rmssd: Double,
        count: Int = 300
    ): List<Double> {
        val meanRRI = 60000.0 / meanHr // Convert HR to RR interval
        val intervals = mutableListOf<Double>()

        // Start with mean RRI
        intervals.add(meanRRI)

        // Generate successive differences with target RMSSD
        val random = java.util.Random()
        for (i in 1 until count) {
            // Generate diff with normal distribution
            val diff = random.nextGaussian() * (rmssd / kotlin.math.sqrt(2.0))
            var nextRRI = intervals.last() + diff

            // Keep within physiological range (300-2000ms)
            nextRRI = nextRRI.coerceIn(300.0, 2000.0)
            intervals.add(nextRRI)
        }

        return intervals
    }

    /**
     * Observe HRV data changes
     */
    fun observeHrvData(): Flow<HrvData?> {
        return healthConnectManager.observeHrvData()
    }

    fun close() {
        apiClient.close()
    }
}
