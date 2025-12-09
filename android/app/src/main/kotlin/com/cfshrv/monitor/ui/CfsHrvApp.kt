package com.cfshrv.monitor.ui

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.cfshrv.monitor.ui.screens.home.HomeScreen
import com.cfshrv.monitor.ui.screens.setup.SetupScreen

@Composable
fun CfsHrvApp() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "setup"
    ) {
        composable("setup") {
            SetupScreen(
                onSetupComplete = {
                    navController.navigate("home") {
                        popUpTo("setup") { inclusive = true }
                    }
                }
            )
        }

        composable("home") {
            HomeScreen()
        }
    }
}
