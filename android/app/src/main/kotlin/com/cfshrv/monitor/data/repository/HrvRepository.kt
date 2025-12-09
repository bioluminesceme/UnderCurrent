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
     * Sync latest HRV data from Health Connect to backend
     *
     * Note: This is a simplified version that uses RMSSD directly.
     * For full frequency domain analysis, you would need raw RR intervals.
     */
    suspend fun syncLatestHrvToBackend(userId: Int): Result<EnergyBudgetResponse> {
        return try {
            // Get latest HRV data from Health Connect
            val hrvData = healthConnectManager.getLatestHrvData()
                ?: return Result.failure(Exception("No HRV data available"))

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

            val readingResult = apiClient.submitHrvReading(userId, request)
            if (readingResult.isFailure) {
                return Result.failure(readingResult.exceptionOrNull()!!)
            }

            val reading = readingResult.getOrThrow()

            // Calculate readiness score
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
