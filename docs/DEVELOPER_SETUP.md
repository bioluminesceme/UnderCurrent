# Developer Setup Guide

This guide is for developers who want to build and modify UnderCurrent from source.

**For end users:** Just download the APK from [GitHub Releases](https://github.com/yourusername/undercurrent/releases) - no setup required!

---

## Prerequisites

- Python 3.8+ with [uv](https://docs.astral.sh/uv/)
- Android Studio (latest version)
- A Garmin Connect account
- Garmin Connect Developer Program API access

---

## Step 1: Get Garmin API Credentials

1. Go to [Garmin Connect Developer Program](https://developer.garmin.com/gc-developer-program/)
2. Create an account or sign in
3. Fill out the application form (see GARMIN_APPLICATION.md for tips)
4. Wait for approval (usually a few days)
5. Once approved, get your **Consumer Key** and **Consumer Secret**

---

## Step 2: Backend Setup

### 2.1 Clone the Repository

```bash
git clone https://github.com/yourusername/undercurrent.git
cd undercurrent
```

### 2.2 Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your favorite editor
# Add your Garmin API credentials and generate a secret key
```

**Generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

**Your .env should look like:**
```env
GARMIN_API_KEY=your_actual_consumer_key_from_garmin
GARMIN_API_SECRET=your_actual_consumer_secret_from_garmin
SECRET_KEY=generated_secret_key_from_openssl_command
```

### 2.3 Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2.4 Generate SSL Certificates

```bash
cd certs
openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365 -config openssl.cnf

# Update openssl.cnf if you need to change the IP address
```

### 2.5 Run the Backend

```bash
uv run python run_server.py
```

The backend should now be running at `https://localhost:4777`

Test it by visiting: `https://localhost:4777/docs` (accept the certificate warning)

---

## Step 3: Android App Setup

### 3.1 Open in Android Studio

1. Launch Android Studio
2. Open the `android/` directory as a project
3. Wait for Gradle sync to complete

### 3.2 Configure API Credentials

```bash
# From the android/ directory
cp local.properties.example local.properties
```

Edit `local.properties` and add your Garmin credentials:
```properties
garmin.api.key=your_garmin_consumer_key
garmin.api.secret=your_garmin_consumer_secret
backend.url=https://10.0.2.2:4777/api
```

**OR** use the ApiConfig approach:

```bash
cd android/app/src/main/kotlin/com/cfshrv/monitor/config/
cp ApiConfig.kt.example ApiConfig.kt
```

Edit `ApiConfig.kt` with your credentials.

### 3.3 Update Backend URL

- **For Android Emulator:** Use `https://10.0.2.2:4777/api`
- **For Physical Device:** Use `https://YOUR_COMPUTER_IP:4777/api`

Find your computer's IP:
```bash
# Windows
ipconfig

# Mac/Linux
ifconfig
# or
ip addr show
```

### 3.4 Build and Run

1. Connect your Android device or start an emulator
2. Click **Run** in Android Studio (green play button)
3. Or use command line:
   ```bash
   ./gradlew installDebug
   ```

---

## Step 4: Testing the Complete Flow

1. **Start the backend:**
   ```bash
   uv run python run_server.py
   ```

2. **Run the Android app** on your device/emulator

3. **Test with sample data:**
   ```bash
   uv run python test_api.py
   ```

4. **Create demo user:**
   ```bash
   uv run python setup_test_data.py
   ```

---

## Project Structure

```
UnderCurrent/
├── backend/                    # Python FastAPI backend
│   ├── api/                   # API endpoints
│   ├── models.py              # Database models
│   ├── hrv_calculator.py      # HRV calculations
│   └── energy_budget_calculator.py
├── android/                    # Android app
│   ├── app/src/main/kotlin/   # Kotlin source code
│   └── local.properties       # API keys (gitignored)
├── certs/                      # SSL certificates
│   ├── cert.pem               # Self-signed cert (gitignored)
│   └── key.pem                # Private key (gitignored)
├── .env                        # Environment variables (gitignored)
├── .env.example                # Template for .env
└── run_server.py               # Backend entry point
```

---

## Common Issues

### "SSL Certificate Verification Failed"

This is normal for self-signed certificates. The app is configured to accept them for local development.

### "Connection Refused" from Android App

- Check that backend is running: `https://localhost:4777/docs`
- Verify correct IP address in Android app config
- Ensure firewall allows port 4777
- Confirm both devices on same WiFi network (for physical devices)

### Garmin API Returns 401 Unauthorized

- Double-check your API credentials in `.env`
- Verify OAuth callback URL matches what you registered with Garmin
- Check that your Garmin Developer account is approved

### "Module not found" Errors in Python

```bash
# Reinstall dependencies
uv sync --force
```

---

## Building for Distribution

### Create Release APK

```bash
cd android
./gradlew assembleRelease
```

The APK will be in: `android/app/build/outputs/apk/release/`

**Important:** Your Garmin API credentials will be embedded in this APK. This is normal and allows end users to use your app without their own API key.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Code style
- Submitting pull requests
- Running tests
- Reporting bugs

---

## Security Notes

**DO NOT commit:**
- `.env` file (contains your Garmin API secrets)
- `local.properties` (contains API keys)
- `ApiConfig.kt` (contains API keys)
- `certs/*.pem` (SSL certificates)

All of these are in `.gitignore` and should never be pushed to GitHub.

---

## Need Help?

- **Bug reports:** [GitHub Issues](https://github.com/yourusername/undercurrent/issues)
- **Questions:** [GitHub Discussions](https://github.com/yourusername/undercurrent/discussions)
- **Garmin API docs:** [Garmin Developer Portal](https://developer.garmin.com/)

---

## License

AGPL-3.0 - See [LICENSE](LICENSE) file for details.
