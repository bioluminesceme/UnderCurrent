package com.cfshrv.monitor.ui.screens.home

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.health.connect.client.HealthConnectClient
import androidx.lifecycle.viewmodel.compose.viewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = viewModel(
        factory = HomeViewModelFactory(LocalContext.current.applicationContext as android.app.Application)
    )
) {
    val context = LocalContext.current
    var selectedTab by remember { mutableStateOf(0) }
    val uiState by viewModel.uiState.collectAsState()

    // Health Connect permission launcher
    val permissionLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
        contract = androidx.health.connect.client.PermissionController.createRequestPermissionResultContract()
    ) { granted ->
        android.util.Log.d("HomeScreen", "Permissions result: $granted")
        android.util.Log.d("HomeScreen", "Granted permissions count: ${granted.size}")
        granted.forEach { permission ->
            android.util.Log.d("HomeScreen", "Granted: $permission")
        }
        // Refresh Health Connect status after permissions are granted
        viewModel.checkHealthConnect()

        // If permissions were granted, try syncing
        if (granted.isNotEmpty()) {
            viewModel.syncData()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("UnderCurrent") },
                actions = {
                    IconButton(onClick = { /* Settings */ }) {
                        Icon(Icons.Default.Settings, "Settings")
                    }
                }
            )
        },
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    icon = { Icon(Icons.Default.Home, "Home") },
                    label = { Text("Today") }
                )
                NavigationBarItem(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    icon = { Icon(Icons.Default.TrendingUp, "Trend") },
                    label = { Text("Trends") }
                )
                NavigationBarItem(
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 },
                    icon = { Icon(Icons.Default.Sync, "Sync") },
                    label = { Text("Sync") }
                )
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            when (selectedTab) {
                0 -> TodayTab(uiState)
                1 -> TrendsTab()
                2 -> SyncTab(
                    isSyncing = uiState.isSyncing,
                    lastSyncTime = uiState.lastSyncTime,
                    error = uiState.error,
                    healthConnectAvailable = uiState.healthConnectAvailable,
                    onSyncClick = { viewModel.syncData() },
                    onTestSync = { viewModel.testSyncWithDemoData() },
                    onRequestPermissions = {
                        android.util.Log.d("HomeScreen", "Permission button clicked")
                        // Always try to request permissions directly
                        // If HC is not installed, this will fail gracefully
                        try {
                            android.util.Log.d("HomeScreen", "Launching permission request")
                            permissionLauncher.launch(
                                com.cfshrv.monitor.data.healthconnect.HealthConnectManager.PERMISSIONS
                            )
                        } catch (e: Exception) {
                            android.util.Log.e("HomeScreen", "Permission request failed", e)
                            // If permission request fails, open Play Store
                            val intent = Intent(Intent.ACTION_VIEW).apply {
                                data = Uri.parse("market://details?id=com.google.android.apps.healthdata")
                            }
                            try {
                                context.startActivity(intent)
                            } catch (ex: Exception) {
                                android.util.Log.e("HomeScreen", "Failed to open Play Store", ex)
                            }
                        }
                    }
                )
            }
        }
    }
}

@Composable
private fun TodayTab(uiState: HomeUiState) {
    // Use real data if available, otherwise show demo data
    val energyBudget = uiState.energyBudget
    val readinessScore = energyBudget?.readinessScore ?: 72.0
    val hrvScore = energyBudget?.hrvScore ?: 68.0
    val rhrScore = energyBudget?.rhrScore ?: 75.0
    val sleepScore = energyBudget?.sleepScore ?: 70.0
    val stressScore = energyBudget?.stressScore ?: 80.0
    val pemRisk = energyBudget?.pemRiskLevel ?: "low"
    val recommendation = energyBudget?.activityRecommendation ?: "normal"

    if (energyBudget == null && !uiState.isLoading) {
        // Show message if no data yet
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    "No data yet - go to Sync tab to get started!",
                    style = MaterialTheme.typography.bodyLarge,
                    textAlign = TextAlign.Center
                )
            }
        }
        Spacer(modifier = Modifier.height(16.dp))
    }

    Text(
        text = "Today's Energy Budget",
        style = MaterialTheme.typography.headlineMedium
    )

    // Energy Budget Card
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = getReadinessColor(readinessScore)
        )
    ) {
        Column(
            modifier = Modifier.padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "${readinessScore.toInt()}",
                style = MaterialTheme.typography.displayLarge,
                color = Color.White
            )
            Text(
                text = "Energy Budget",
                style = MaterialTheme.typography.titleMedium,
                color = Color.White
            )
        }
    }

    // Activity Recommendation
    Card(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                getRecommendationIcon(recommendation),
                contentDescription = null,
                modifier = Modifier.size(48.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(
                    text = "Activity Level",
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = recommendation.replaceFirstChar { it.uppercase() },
                    style = MaterialTheme.typography.bodyLarge,
                    color = getRecommendationColor(recommendation)
                )
            }
        }
    }

    // Component Scores
    Text(
        text = "Component Scores",
        style = MaterialTheme.typography.titleLarge
    )

    ScoreRow("HRV", hrvScore)
    ScoreRow("Resting HR", rhrScore)
    ScoreRow("Sleep", sleepScore)
    ScoreRow("Stress", stressScore)

    // PEM Risk
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = getPemRiskColor(pemRisk)
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "PEM Risk: ${pemRisk.uppercase()}",
                style = MaterialTheme.typography.titleMedium,
                color = Color.White
            )
        }
    }
}

@Composable
private fun TrendsTab() {
    Text(
        text = "7-Day Trend",
        style = MaterialTheme.typography.headlineMedium
    )

    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("Chart visualization would go here")
            Text(
                text = "Track your readiness scores over time",
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
private fun SyncTab(
    isSyncing: Boolean,
    lastSyncTime: String?,
    error: String?,
    healthConnectAvailable: Boolean,
    onSyncClick: () -> Unit,
    onTestSync: () -> Unit,
    onRequestPermissions: () -> Unit
) {
    val context = LocalContext.current

    Text(
        text = "Sync Data",
        style = MaterialTheme.typography.headlineMedium
    )

    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Icon(
                Icons.Default.Sync,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = if (isSyncing) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
            )

            Text(
                text = "Sync HRV data from Health Connect",
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center
            )

            // Permission request buttons
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "Grant Health Connect permissions:",
                    style = MaterialTheme.typography.bodyMedium,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth()
                )

                // Primary button: Open Health Connect permissions for our app
                Button(
                    onClick = {
                        android.util.Log.d("HomeScreen", "Opening Health Connect permissions...")
                        try {
                            // Try to open Health Connect permission screen directly
                            val intent = Intent("androidx.health.ACTION_REQUEST_PERMISSIONS").apply {
                                setPackage("com.google.android.apps.healthdata")
                                putExtra("android.intent.extra.PACKAGE_NAME", context.packageName)
                            }
                            context.startActivity(intent)
                        } catch (e: Exception) {
                            android.util.Log.e("HomeScreen", "Failed to open HC permissions, trying launcher", e)
                            // Fallback: just request permissions normally
                            onRequestPermissions()
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.primary
                    )
                ) {
                    Text("Open Health Permissions")
                }

                // Secondary button: Open Health Connect app
                Button(
                    onClick = {
                        android.util.Log.d("HomeScreen", "Opening Health Connect app directly")
                        try {
                            // Try to open Health Connect app directly
                            val intent = context.packageManager.getLaunchIntentForPackage(
                                "com.google.android.apps.healthdata"
                            )
                            if (intent != null) {
                                context.startActivity(intent)
                            } else {
                                // Fallback: open Play Store
                                val playIntent = Intent(Intent.ACTION_VIEW).apply {
                                    data = Uri.parse("market://details?id=com.google.android.apps.healthdata")
                                }
                                context.startActivity(playIntent)
                            }
                        } catch (e: Exception) {
                            android.util.Log.e("HomeScreen", "Failed to open Health Connect", e)
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.secondary
                    )
                ) {
                    Text("Open Health Connect App")
                }

                Text(
                    text = "If button doesn't work: Open Health Connect → App permissions → UnderCurrent → Allow all",
                    style = MaterialTheme.typography.bodySmall,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth()
                )
            }


            if (error != null) {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(8.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "Error: $error",
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            style = MaterialTheme.typography.bodySmall
                        )

                        if (error.contains("permissions", ignoreCase = true)) {
                            Button(
                                onClick = onRequestPermissions,
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = MaterialTheme.colorScheme.error
                                )
                            ) {
                                Text("Grant Health Connect Permissions")
                            }
                        }
                    }
                }
            }

            if (isSyncing) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    )
                ) {
                    Text(
                        text = "Syncing...",
                        modifier = Modifier.padding(16.dp),
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            } else {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = onSyncClick,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Default.Refresh, contentDescription = null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Sync Now (requires Health Connect)")
                    }

                    Button(
                        onClick = onTestSync,
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.tertiary
                        )
                    ) {
                        Text("Test Sync (Demo Data)")
                    }
                }
            }

            Text(
                text = "Last sync: ${lastSyncTime ?: "Never"}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun ScoreRow(label: String, score: Double) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyLarge
            )
            Text(
                text = "${score.toInt()}/100",
                style = MaterialTheme.typography.titleMedium,
                color = getScoreColor(score)
            )
        }
    }
}

private fun getReadinessColor(score: Double): Color {
    return when {
        score >= 70 -> Color(0xFF4CAF50) // Green
        score >= 50 -> Color(0xFFFFC107) // Amber
        score >= 30 -> Color(0xFFFF9800) // Orange
        else -> Color(0xFFF44336) // Red
    }
}

private fun getScoreColor(score: Double): Color {
    return when {
        score >= 70 -> Color(0xFF4CAF50)
        score >= 50 -> Color(0xFFFFC107)
        else -> Color(0xFFFF9800)
    }
}

private fun getPemRiskColor(risk: String): Color {
    return when (risk.lowercase()) {
        "low" -> Color(0xFF4CAF50)
        "moderate" -> Color(0xFFFFC107)
        "high" -> Color(0xFFF44336)
        else -> Color.Gray
    }
}

private fun getRecommendationColor(rec: String): Color {
    return when (rec.lowercase()) {
        "normal" -> Color(0xFF4CAF50)
        "light" -> Color(0xFF8BC34A)
        "reduced" -> Color(0xFFFFC107)
        "rest" -> Color(0xFFF44336)
        else -> Color.Gray
    }
}

private fun getRecommendationIcon(rec: String) = when (rec.lowercase()) {
    "normal" -> Icons.Default.DirectionsRun
    "light" -> Icons.Default.DirectionsWalk
    "reduced" -> Icons.Default.SelfImprovement
    "rest" -> Icons.Default.Hotel
    else -> Icons.Default.Help
}
