package com.cfshrv.monitor.data.api

import android.util.Log
import com.cfshrv.monitor.data.model.*
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.android.*
import io.ktor.client.plugins.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.logging.*
import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json

/**
 * API client for CFS-HRV Monitor backend.
 * Communicates with FastAPI backend running on port 4777.
 */
class CfsHrvApiClient(
    private val baseUrl: String = "http://192.168.2.9:4777/api" // Local network IP
) {
    companion object {
        private const val TAG = "CfsHrvApiClient"
    }

    private val client = HttpClient(Android) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
                prettyPrint = true
            })
        }

        install(Logging) {
            logger = object : Logger {
                override fun log(message: String) {
                    Log.d(TAG, message)
                }
            }
            level = LogLevel.INFO
        }

        install(HttpTimeout) {
            requestTimeoutMillis = 30_000
            connectTimeoutMillis = 15_000
        }

        defaultRequest {
            contentType(ContentType.Application.Json)
        }
    }

    /**
     * Create a new user account
     */
    suspend fun createUser(request: UserCreateRequest): Result<UserResponse> {
        return try {
            val response = client.post("$baseUrl/users/") {
                setBody(request)
            }
            Result.success(response.body())
        } catch (e: Exception) {
            Log.e(TAG, "Error creating user", e)
            Result.failure(e)
        }
    }

    /**
     * Get user by ID
     */
    suspend fun getUser(userId: Int): Result<UserResponse> {
        return try {
            val response = client.get("$baseUrl/users/$userId")
            Result.success(response.body())
        } catch (e: Exception) {
            Log.e(TAG, "Error getting user", e)
            Result.failure(e)
        }
    }

    /**
     * Submit RR intervals for HRV calculation
     */
    suspend fun submitHrvReading(
        userId: Int,
        request: RRIntervalsRequest
    ): Result<HrvReadingResponse> {
        return try {
            val response = client.post("$baseUrl/hrv/$userId/readings") {
                setBody(request)
            }
            Result.success(response.body())
        } catch (e: Exception) {
            Log.e(TAG, "Error submitting HRV reading", e)
            Result.failure(e)
        }
    }

    /**
     * Get recent HRV readings for user
     */
    suspend fun getHrvReadings(
        userId: Int,
        limit: Int = 30
    ): Result<List<HrvReadingResponse>> {
        return try {
            val response = client.get("$baseUrl/hrv/$userId/readings") {
                parameter("limit", limit)
            }
            Result.success(response.body())
        } catch (e: Exception) {
            Log.e(TAG, "Error getting HRV readings", e)
            Result.failure(e)
        }
    }

    /**
     * Calculate and save baseline for user
     */
    suspend fun calculateBaseline(userId: Int): Result<BaselineResponse> {
        return try {
            val response = client.post("$baseUrl/energy-budget/$userId/baseline")
            Result.success(response.body())
        } catch (e: Exception) {
            Log.e(TAG, "Error calculating baseline", e)
            Result.failure(e)
        }
    }

    /**
     * Get active baseline for user
     */
    suspend fun getActiveBaseline(userId: Int): Result<BaselineResponse> {
        return try {
            val response = client.get("$baseUrl/energy-budget/$userId/baseline")
            Result.success(response.body())
        } catch (e: Exception) {
            Log.e(TAG, "Error getting baseline", e)
            Result.failure(e)
        }
    }

    /**
     * Calculate readiness score from HRV reading
     */
    suspend fun calculateEnergyBudget(
        userId: Int,
        readingId: Int
    ): Result<EnergyBudgetResponse> {
        return try {
            val response = client.post("$baseUrl/energy-budget/$userId/energy-budget/$readingId")
            Result.success(response.body())
        } catch (e: Exception) {
            Log.e(TAG, "Error calculating readiness score", e)
            Result.failure(e)
        }
    }

    /**
     * Get recent readiness scores
     */
    suspend fun getEnergyBudgets(
        userId: Int,
        limit: Int = 30
    ): Result<List<EnergyBudgetResponse>> {
        return try {
            val response = client.get("$baseUrl/energy-budget/$userId/readiness") {
                parameter("limit", limit)
            }
            Result.success(response.body())
        } catch (e: Exception) {
            Log.e(TAG, "Error getting readiness scores", e)
            Result.failure(e)
        }
    }

    /**
     * Get readiness trend over specified days
     */
    suspend fun getEnergyBudgetTrend(
        userId: Int,
        days: Int = 7
    ): Result<List<Map<String, Any>>> {
        return try {
            val response = client.get("$baseUrl/energy-budget/$userId/energy-budget/trend/$days")
            Result.success(response.body())
        } catch (e: Exception) {
            Log.e(TAG, "Error getting readiness trend", e)
            Result.failure(e)
        }
    }

    /**
     * Close the HTTP client
     */
    fun close() {
        client.close()
    }
}
