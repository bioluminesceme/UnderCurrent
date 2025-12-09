package com.cfshrv.monitor.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import java.time.Instant

/**
 * Local HRV data collected from Health Connect
 */
data class HrvData(
    val timestamp: Instant,
    val rmssdMs: Double,
    val heartRateBpm: Double,
    val sleepDurationHours: Double? = null,
    val sleepQualityScore: Double? = null
)

/**
 * API request model for submitting RR intervals
 */
@Serializable
data class RRIntervalsRequest(
    @SerialName("rr_intervals")
    val rrIntervals: List<Double>,
    @SerialName("recorded_at")
    val recordedAt: String,  // ISO 8601 format
    @SerialName("sleep_duration")
    val sleepDuration: Double? = null,
    @SerialName("sleep_quality")
    val sleepQuality: Double? = null
)

/**
 * API response model for HRV reading
 */
@Serializable
data class HrvReadingResponse(
    val id: Int,
    @SerialName("user_id")
    val userId: Int,
    @SerialName("recorded_at")
    val recordedAt: String,
    @SerialName("mean_rri")
    val meanRri: Double? = null,
    @SerialName("mean_hr")
    val meanHr: Double? = null,
    val sdnn: Double? = null,
    val rmssd: Double? = null,
    val pnn50: Double? = null,
    @SerialName("vlf_power")
    val vlfPower: Double? = null,
    @SerialName("lf_power")
    val lfPower: Double? = null,
    @SerialName("hf_power")
    val hfPower: Double? = null,
    @SerialName("total_power")
    val totalPower: Double? = null,
    @SerialName("lf_hf_ratio")
    val lfHfRatio: Double? = null
)

/**
 * API response model for readiness score
 */
@Serializable
data class EnergyBudgetResponse(
    val id: Int,
    val date: String,
    @SerialName("energy_budget")
    val readinessScore: Double,
    @SerialName("hrv_score")
    val hrvScore: Double,
    @SerialName("rhr_score")
    val rhrScore: Double,
    @SerialName("sleep_score")
    val sleepScore: Double,
    @SerialName("stress_score")
    val stressScore: Double,
    @SerialName("hrv_zscore")
    val hrvZscore: Double,
    @SerialName("rhr_zscore")
    val rhrZscore: Double,
    @SerialName("pem_risk_level")
    val pemRiskLevel: String,
    @SerialName("consecutive_low_days")
    val consecutiveLowDays: Int,
    @SerialName("activity_recommendation")
    val activityRecommendation: String
)

/**
 * API response model for baseline
 */
@Serializable
data class BaselineResponse(
    val id: Int,
    @SerialName("calculated_at")
    val calculatedAt: String,
    @SerialName("start_date")
    val startDate: String,
    @SerialName("end_date")
    val endDate: String,
    @SerialName("days_count")
    val daysCount: Int,
    @SerialName("mean_ln_rmssd")
    val meanLnRmssd: Double,
    @SerialName("sd_ln_rmssd")
    val sdLnRmssd: Double,
    @SerialName("mean_rmssd")
    val meanRmssd: Double,
    @SerialName("mean_hr")
    val meanHr: Double? = null,
    @SerialName("sd_hr")
    val sdHr: Double? = null
)

/**
 * User creation request
 */
@Serializable
data class UserCreateRequest(
    val email: String,
    val password: String,
    val age: Int? = null,
    val sex: String? = null,
    val bmi: Double? = null
)

/**
 * User response
 */
@Serializable
data class UserResponse(
    val id: Int,
    val email: String,
    val age: Int? = null,
    val sex: String? = null,
    val bmi: Double? = null,
    @SerialName("created_at")
    val createdAt: String
)
