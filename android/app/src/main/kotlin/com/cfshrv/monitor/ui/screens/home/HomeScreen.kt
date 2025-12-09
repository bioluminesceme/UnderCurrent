package com.cfshrv.monitor.ui.screens.home

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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen() {
    var selectedTab by remember { mutableStateOf(0) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("CFS-HRV Monitor") },
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
                0 -> TodayTab()
                1 -> TrendsTab()
                2 -> SyncTab()
            }
        }
    }
}

@Composable
private fun TodayTab() {
    // Mock data for demonstration
    val readinessScore = 72.0
    val hrvScore = 68.0
    val rhrScore = 75.0
    val sleepScore = 70.0
    val stressScore = 80.0
    val pemRisk = "low"
    val recommendation = "normal"

    Text(
        text = "Today's Readiness",
        style = MaterialTheme.typography.headlineMedium
    )

    // Readiness Score Card
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
                text = "Readiness Score",
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
private fun SyncTab() {
    var syncing by remember { mutableStateOf(false) }

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
                modifier = Modifier.size(64.dp)
            )

            Text(
                text = "Sync HRV data from Health Connect",
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center
            )

            if (syncing) {
                CircularProgressIndicator()
                Text("Syncing...")
            } else {
                Button(
                    onClick = { syncing = true },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(Icons.Default.Refresh, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Sync Now")
                }
            }

            Text(
                text = "Last sync: Never",
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
