# Android App Setup Guide

## Prerequisites
- Android Studio (latest version)
- Physical Android device or emulator (Android 8.0+ / API 26+)
- USB debugging enabled on your phone

## Step 1: Install Android Studio
Download from: https://developer.android.com/studio

## Step 2: Open Project
1. Open Android Studio
2. Click "Open an Existing Project"
3. Navigate to `F:/UnderCurrentAppPaxum/android`
4. Wait for Gradle sync to complete

## Step 3: Generate App Icons (Temporary)
The app currently has placeholder icon config but needs actual icon images.

**Quick fix for testing:**
1. In Android Studio, right-click `res` folder
2. Select New → Image Asset
3. Choose "Launcher Icons (Adaptive and Legacy)"
4. Use default settings
5. Click "Next" then "Finish"

**Or manually:**
Use any square PNG image and place copies in:
- `res/mipmap-mdpi/ic_launcher.png` (48x48)
- `res/mipmap-hdpi/ic_launcher.png` (72x72)
- `res/mipmap-xhdpi/ic_launcher.png` (96x96)
- `res/mipmap-xxhdpi/ic_launcher.png` (144x144)
- `res/mipmap-xxxhdpi/ic_launcher.png` (192x192)

## Step 4: Connect to Your Backend

### Option A: Local Backend (Phone on Same WiFi)
1. Find your computer's local IP address:
   ```bash
   # Windows
   ipconfig
   # Look for "IPv4 Address" (e.g., 192.168.1.100)

   # Linux/Mac
   ifconfig
   # or
   ip addr show
   ```

2. Update API base URL in Android app:
   - Open `android/app/src/main/kotlin/com/cfshrv/monitor/data/api/CfsHrvApiClient.kt`
   - Change `baseUrl` from `https://10.0.2.2:4777/api` to `https://YOUR_IP:4777/api`
   - Example: `https://192.168.1.100:4777/api`

### Option B: Using Android Emulator
- Keep the default `https://10.0.2.2:4777/api`
- `10.0.2.2` is the emulator's special alias for host machine's localhost

**Note:** The app uses HTTPS with a self-signed certificate. The Android client is configured to accept this for local development.

## Step 5: Install Health Connect
On your phone (not emulator):
1. Open Google Play Store
2. Search for "Health Connect by Google"
3. Install it
4. Open and complete setup

**Note:** Health Connect is not available on emulators! You need a physical device.

## Step 6: Build and Install

### Using Android Studio:
1. Connect your phone via USB
2. Enable "USB Debugging" in phone's Developer Options
3. Click the "Run" button (green triangle) in Android Studio
4. Select your device
5. Wait for build and installation

### Using Command Line:
```bash
cd android
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Step 7: Grant Permissions
When you first open the app:
1. Complete the setup wizard
2. When prompted, grant Health Connect permissions:
   - Heart Rate Variability (RMSSD)
   - Heart Rate
   - Sleep Data

## Step 8: Test the Flow
1. Ensure your backend is running: `uv run python run_server.py`
2. Ensure you have HRV data in Health Connect (from Garmin/Fitbit watch)
3. Open the app
4. Go to "Sync" tab
5. Tap "Sync Now"
6. Check backend logs to see data being received

## Troubleshooting

### "Cannot resolve symbol" errors in Android Studio
Run: Tools → Kotlin → Configure Kotlin Plugin Updates

### "Health Connect not found"
- Only works on Android 9+ (API 28+)
- Install "Health Connect by Google" from Play Store
- Not available on emulators

### Connection to backend fails
- Check your phone is on same WiFi as computer
- Verify backend is running: https://YOUR_IP:4777/docs (accept self-signed certificate warning)
- Check firewall isn't blocking port 4777
- For Windows: Allow Python through Windows Firewall

### No HRV data available
- Connect your Garmin/Fitbit watch to phone
- Ensure watch has synced to Garmin Connect / Fitbit app
- Ensure Garmin Connect / Fitbit app is writing to Health Connect
- Check Health Connect app → Data and Access → [Your Watch App]

## Current Limitations (Phase 1)

1. **Synthetic RR Intervals**: The app generates RR intervals from RMSSD because Health Connect doesn't expose raw RR intervals on most devices
2. **No Authentication**: User management is basic (no login required yet)
3. **Mock UI Data**: Some UI elements show placeholder data
4. **No Charts**: Trend visualization not implemented yet

These will be addressed in Phase 2!

## Next: Connecting Your Watch

See `WATCH_SYNC_GUIDE.md` for watch-specific instructions.
