# Watch → Phone → Backend Sync Guide

## The Data Flow

```
Garmin/Fitbit Watch
    ↓ (Bluetooth sync during sleep)
Garmin Connect / Fitbit App
    ↓ (Writes to Health Connect)
Health Connect (Android)
    ↓ (Your app reads from)
CFS-HRV Monitor App
    ↓ (Uploads to)
Backend API (localhost:4777)
    ↓ (Calculates)
Energy Budget Score
```

## Supported Devices

### ✅ Confirmed Working:
- **Garmin Watches** (most models with HRV tracking):
  - Fenix series (6, 7, 8)
  - Forerunner series (245, 255, 265, 945, 955, 965)
  - Venu series (2, 3)
  - Epix series
  - Any Garmin with "Body Battery" feature

- **Fitbit Watches** (with HRV tracking):
  - Sense
  - Versa 3/4
  - Charge 5/6
  - Pixel Watch

### ⚠️ Limited Support:
- Apple Watch: Requires different approach (not Health Connect)
- Samsung Galaxy Watch: Should work via Health Connect
- Polar watches: Limited Health Connect support

## Step-by-Step Setup

### 1. Enable HRV Tracking on Your Watch

#### Garmin:
1. Open Garmin Connect app
2. Go to Settings → User Settings → Health Stats
3. Enable "All Day Stress Tracking"
4. Enable "Pulse Ox" (if available)
5. Sync your watch

Your watch will automatically track HRV during sleep.

#### Fitbit:
1. Open Fitbit app
2. Go to Today tab → Profile → [Your Watch]
3. Enable "Heart Rate Variability"
4. Sync your watch

### 2. Connect Watch App to Health Connect

#### Garmin Connect → Health Connect:
1. Open Garmin Connect app
2. Go to Settings → Health Connect
3. Tap "Connect to Health Connect"
4. Grant all permissions when prompted:
   - ✅ Heart Rate
   - ✅ Heart Rate Variability
   - ✅ Sleep
5. Tap "Allow access"

#### Fitbit → Health Connect:
1. Open Fitbit app
2. Go to Settings → Health Connect
3. Tap "Connect"
4. Grant permissions

### 3. Verify Data is Flowing

#### Check Health Connect:
1. Open Health Connect app
2. Go to "Browse data"
3. Look for:
   - Heart Rate Variability (should have recent readings)
   - Heart Rate
   - Sleep sessions

If you see data here, you're good! ✅

### 4. Configure Your App for WiFi Access

Your phone needs to reach your computer's backend API.

#### Find Your Computer's IP:
**Windows:**
```bash
ipconfig
# Look for "IPv4 Address" under your WiFi adapter
# Example: 192.168.1.100
```

**Mac/Linux:**
```bash
ifconfig
# or
ip addr show
```

#### Update the App:
Open this file in Android Studio:
```
android/app/src/main/kotlin/com/cfshrv/monitor/data/api/CfsHrvApiClient.kt
```

Change line ~20:
```kotlin
private val baseUrl: String = "http://YOUR_IP_HERE:4777/api"
// Example: "http://192.168.1.100:4777/api"
```

**Important:** Use your actual IP, not `localhost` or `127.0.0.1`!

### 5. Test the Full Flow

1. **Wear your watch overnight** with HRV tracking enabled
2. **Next morning:**
   - Ensure watch syncs to phone (Garmin Connect/Fitbit app)
   - Wait 1-2 minutes for data to propagate to Health Connect
3. **Start your backend:**
   ```bash
   cd F:/UnderCurrentAppPaxum
   uv run python run_server.py
   ```
4. **Open your app** on phone
5. **Go to "Sync" tab**
6. **Tap "Sync Now"**
7. **Check backend terminal** - you should see:
   ```
   INFO: POST /api/hrv/{user_id}/readings
   INFO: POST /api/energy-budget/{user_id}/energy-budget/{reading_id}
   ```

## Troubleshooting

### "No HRV data available"

**Check 1:** Does your watch support HRV?
- Garmin: Look for "Body Battery" or "Stress" features
- Fitbit: Check if your model supports HRV

**Check 2:** Is HRV tracking enabled?
- Enable "All Day Stress" (Garmin) or "HRV tracking" (Fitbit)

**Check 3:** Did you wear it overnight?
- HRV is primarily measured during sleep
- Wait until after you wake up

**Check 4:** Is watch synced?
- Open Garmin Connect / Fitbit app
- Manually trigger sync if needed

**Check 5:** Is data in Health Connect?
- Open Health Connect app
- Browse data → Heart Rate Variability
- Should show recent measurements

### "Connection to backend failed"

**Check 1:** Is backend running?
```bash
# In your computer terminal:
uv run python run_server.py
# Should show: "Uvicorn running on http://0.0.0.0:4777"
```

**Check 2:** Can you reach it from phone's browser?
- Open Chrome on your phone
- Visit: `http://YOUR_IP:4777/docs`
- Should show Swagger API docs

**Check 3:** Are phone and computer on same WiFi?
- Both must be on the same network
- No VPN running on either

**Check 4:** Is firewall blocking?
- Windows: Allow Python through Windows Defender Firewall
- Mac: System Preferences → Security → Firewall → Allow incoming connections

### "Health Connect permissions denied"

**Solution:**
1. Open Settings on phone
2. Apps → Health Connect
3. App permissions → CFS HRV Monitor
4. Grant all permissions

## Data Quality Tips

### For Best HRV Readings:
1. **Consistent sleep schedule** - Go to bed/wake at similar times
2. **Wear watch snugly** - Should be firm but comfortable
3. **Charge watch during day** - Wear it at night for HRV tracking
4. **Wait for baseline** - Need 7+ days of data for meaningful Energy Budget
5. **Sync daily** - Build your 28-day baseline gradually

### What to Expect:
- **First week:** App establishes your baseline (no Energy Budget yet)
- **After 7 days:** First Energy Budget score appears
- **After 28 days:** Full baseline established, scores are most accurate
- **Ongoing:** Rolling 28-day window keeps baseline current

## Next Steps

Once data is flowing:
1. Build your 7-day baseline
2. Start getting daily Energy Budget scores
3. Use activity recommendations to pace yourself
4. Monitor for PEM risk indicators

See the main README.md for interpreting your scores!
