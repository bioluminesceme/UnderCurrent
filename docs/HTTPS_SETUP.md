# HTTPS Setup Guide

UnderCurrent now uses HTTPS for all communications between the Android app and backend server.

## Overview

- Backend server uses self-signed SSL certificates
- All HTTP endpoints changed to HTTPS (port 4777)
- Android app configured to accept self-signed certificates for local development
- All test scripts updated to use HTTPS

## Certificate Location

SSL certificates are stored in the `certs/` directory:
- `certs/cert.pem` - Self-signed certificate
- `certs/key.pem` - Private key
- `certs/openssl.cnf` - OpenSSL configuration

These certificates are:
- Valid for 365 days from generation
- Configured for IP: 192.168.2.9, 127.0.0.1, and localhost
- Git-ignored (won't be committed to repository)

## Regenerating Certificates

If you need to regenerate certificates (e.g., changed IP address or expired):

```bash
cd certs
openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365 -config openssl.cnf
```

To change the IP address, edit `certs/openssl.cnf` and update the `CN` field and `alt_names` section.

## Security Notes

**For Local Development Only:**
- The Android app is configured to accept self-signed certificates
- This is ONLY safe for local development on your private network
- Never deploy this configuration to production
- The `TrustAllCerts` implementation in `CfsHrvApiClient.kt` bypasses certificate validation

**Why Self-Signed?**
- Protects data in transit over your local network
- No need for paid certificates for self-hosted use
- Prevents cleartext transmission of health data
- Browser/app warnings are expected and safe to ignore for your own server

## Accessing the Server

### From Your Computer
- API: `https://localhost:4777`
- Docs: `https://localhost:4777/docs`
- Browser will show certificate warning - this is normal, click "Advanced" → "Proceed"

### From Android Device
- API: `https://YOUR_COMPUTER_IP:4777/api` (e.g., `https://192.168.2.9:4777/api`)
- The app automatically accepts the self-signed certificate
- Update `CfsHrvApiClient.kt` with your computer's local IP

### From Python Test Scripts
- All scripts updated to use `https://localhost:4777/api`
- Certificate warnings are disabled with `verify=False` and `urllib3.disable_warnings()`

## Troubleshooting

### "SSL: CERTIFICATE_VERIFY_FAILED"
This means a client is trying to verify the certificate. Solutions:
- **Python scripts**: Use `verify=False` parameter in requests
- **Browser**: Click "Advanced" and proceed (safe for your own server)
- **Android app**: Should work automatically with TrustAllCerts configuration

### "Connection refused" or "Can't connect"
- Check server is running: `uv run python run_server.py`
- Verify using HTTPS not HTTP in URLs
- Check firewall allows port 4777
- Ensure both devices on same network

### Certificate Not Matching IP
If you changed your computer's IP address:
1. Edit `certs/openssl.cnf` to update IP addresses
2. Regenerate certificates (see above)
3. Restart the server

## Files Modified for HTTPS

**Backend:**
- `run_server.py` - Added SSL certificate configuration
- `certs/` - New directory with certificates

**Android:**
- `CfsHrvApiClient.kt` - Changed to HTTPS, added TrustAllCerts
- `BuildConfig.kt.example` - Updated default URL to HTTPS

**Test Scripts:**
- `test_api.py` - HTTPS with verify=False
- `setup_test_data.py` - HTTPS with verify=False
- `create_demo_user.py` - HTTPS with verify=False

**Documentation:**
- `README.md` - Updated URLs and added certificate note
- `ANDROID_SETUP.md` - Updated connection instructions
- `WATCH_SYNC_GUIDE.md` - Updated API URLs
- `.gitignore` - Added certs/*.pem

## Production Considerations

If you ever want to make this production-ready:
1. **Get a real certificate** - Use Let's Encrypt (free) or a paid CA
2. **Remove TrustAllCerts** - Update Android app to use system trust store
3. **Add certificate pinning** - For additional security
4. **Use a domain name** - Instead of IP addresses
5. **Implement authentication** - Add JWT or OAuth2
6. **Review security** - Full security audit before exposing to internet

For self-hosted personal use, the current setup is appropriate.
