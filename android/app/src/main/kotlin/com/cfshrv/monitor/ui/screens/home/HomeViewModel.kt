package com.cfshrv.monitor.ui.screens.home

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.cfshrv.monitor.data.model.EnergyBudgetResponse
import com.cfshrv.monitor.data.repository.HrvRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class HomeUiState(
    val isLoading: Boolean = false,
    val isSyncing: Boolean = false,
    val energyBudget: EnergyBudgetResponse? = null,
    val error: String? = null,
    val lastSyncTime: String? = null,
    val healthConnectAvailable: Boolean = false,
    val hasPermissions: Boolean = false
)

class HomeViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = HrvRepository(application)

    // For demo: using hardcoded user ID until we implement auth
    private val demoUserId = 1

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        checkHealthConnect()
        loadCurrentEnergyBudget()
    }

    fun testSyncWithDemoData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isSyncing = true, error = null)
            android.util.Log.d("HomeViewModel", "Starting test sync with demo data...")

            try {
                // Send synthetic demo data to backend (bypasses Health Connect)
                val result = repository.syncWithDemoData(demoUserId)

                android.util.Log.d("HomeViewModel", "Test sync result: ${result.isSuccess}")

                if (result.isSuccess) {
                    val energyBudget = result.getOrNull()
                    android.util.Log.d("HomeViewModel", "Got energy budget: $energyBudget")
                    _uiState.value = _uiState.value.copy(
                        isSyncing = false,
                        energyBudget = energyBudget,
                        lastSyncTime = java.text.SimpleDateFormat(
                            "HH:mm",
                            java.util.Locale.getDefault()
                        ).format(java.util.Date()),
                        error = null
                    )
                } else {
                    val error = result.exceptionOrNull()
                    android.util.Log.e("HomeViewModel", "Test sync failed", error)
                    _uiState.value = _uiState.value.copy(
                        isSyncing = false,
                        error = "Test sync failed: ${error?.message}"
                    )
                }
            } catch (e: Exception) {
                android.util.Log.e("HomeViewModel", "Test sync error", e)
                _uiState.value = _uiState.value.copy(
                    isSyncing = false,
                    error = "Test error: ${e.message}"
                )
            }
        }
    }

    fun checkHealthConnect() {
        viewModelScope.launch {
            try {
                val available = repository.isHealthConnectReady()
                android.util.Log.d("HomeViewModel", "Health Connect ready: $available")
                _uiState.value = _uiState.value.copy(
                    healthConnectAvailable = available,
                    hasPermissions = available
                )
            } catch (e: Exception) {
                android.util.Log.e("HomeViewModel", "Error checking Health Connect", e)
                _uiState.value = _uiState.value.copy(
                    healthConnectAvailable = false,
                    hasPermissions = false,
                    error = "Error checking Health Connect: ${e.message}"
                )
            }
        }
    }

    fun syncData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isSyncing = true, error = null)
            android.util.Log.d("HomeViewModel", "Starting sync from Health Connect...")

            try {
                // Just try to sync - if we don't have permissions, we'll get a clear error
                android.util.Log.d("HomeViewModel", "Syncing HRV data for user $demoUserId...")

                // Sync HRV data from Health Connect to backend
                val result = repository.syncLatestHrvToBackend(demoUserId)

                android.util.Log.d("HomeViewModel", "Sync result: ${result.isSuccess}")

                if (result.isSuccess) {
                    val energyBudget = result.getOrNull()
                    android.util.Log.d("HomeViewModel", "Energy budget: $energyBudget")
                    _uiState.value = _uiState.value.copy(
                        isSyncing = false,
                        energyBudget = energyBudget,
                        lastSyncTime = java.text.SimpleDateFormat(
                            "HH:mm",
                            java.util.Locale.getDefault()
                        ).format(java.util.Date()),
                        error = null
                    )
                } else {
                    val error = result.exceptionOrNull()
                    android.util.Log.e("HomeViewModel", "Sync failed", error)
                    _uiState.value = _uiState.value.copy(
                        isSyncing = false,
                        error = error?.message ?: "Sync failed"
                    )
                }
            } catch (e: Exception) {
                android.util.Log.e("HomeViewModel", "Sync error", e)
                _uiState.value = _uiState.value.copy(
                    isSyncing = false,
                    error = "Error: ${e.message}"
                )
            }
        }
    }

    fun loadCurrentEnergyBudget() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            val result = repository.getCurrentEnergyBudget(demoUserId)

            if (result.isSuccess) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    energyBudget = result.getOrNull()
                )
            } else {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = result.exceptionOrNull()?.message
                )
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        repository.close()
    }
}
