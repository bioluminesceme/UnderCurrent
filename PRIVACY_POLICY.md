# Privacy Policy for UnderCurrent

**Last Updated:** December 9, 2024

## 1. Introduction

UnderCurrent ("we", "our", or "the app") is committed to protecting your privacy and health data. This Privacy Policy explains how we collect, use, store, and protect your personal health information.

**TL;DR:** Your health data stays on your device and your local server. We don't sell data. We don't track you. Your data is yours.

## 2. Data Controller

**Developer:** [Your Name/Organization]
**Contact:** [Your Email]
**Location:** [Your Location]

For GDPR purposes, you (the user) are both the data controller and data subject when running your own local instance of UnderCurrent.

## 3. What Data We Collect

### 3.1 Health Data
- **Heart Rate Variability (HRV)** or **Resting Heart Rate (RHR)**
- Sleep duration and quality scores
- Heart rate measurements
- Activity levels
- Calculated metrics (z-scores, energy budget scores, PEM risk assessments)

### 3.2 Account Data
- Email address (for account identification only)
- Hashed password (never stored in plain text)
- Account creation timestamp
- User preferences

### 3.3 Technical Data
- App version
- Device type (Android version)
- Error logs (only when crashes occur)

### 3.4 Data We Do NOT Collect
- ❌ Location data
- ❌ Contact lists
- ❌ Photos or media
- ❌ Browsing history
- ❌ Any data from other apps
- ❌ Advertising identifiers
- ❌ Analytics or tracking data

## 4. How We Use Your Data

### 4.1 Primary Uses
- Calculate your personalized 28-day baseline
- Generate daily energy budget scores
- Assess Post-Exertional Malaise (PEM) risk
- Provide activity recommendations
- Track trends over time
- Help you manage ME/CFS symptoms

### 4.2 Data Processing
- All processing happens locally on your device and your local server
- No data is sent to third-party servers
- No data is used for advertising
- No data is sold or shared with third parties

## 5. Data Storage and Security

### 5.1 Local Storage
- **Database:** SQLite database stored on your local server
- **Location:** `F:\UnderCurrentAppPaxum\backend\undercurrent.db`
- **Encryption:** Database at rest (recommended: enable full-disk encryption)
- **Access:** Only accessible from your local network (127.0.0.1 or 192.168.x.x)

### 5.2 Security Measures

#### Authentication
- ✅ Passwords hashed using **bcrypt** (industry-standard)
- ✅ No plain-text password storage
- ✅ Salted hashes (prevents rainbow table attacks)

#### Network Security
- ✅ Local network only (no internet exposure by default)
- ✅ HTTPS recommended (not yet implemented - use reverse proxy)
- ⚠️ Currently uses HTTP over local network (cleartext)

#### Access Control
- ✅ User authentication required for API access
- ✅ Session management (future feature)
- ✅ No cross-origin requests allowed (CORS configured for local only)

#### Data Protection
- ✅ No third-party analytics
- ✅ No advertising SDKs
- ✅ No telemetry or crash reporting to external servers
- ✅ Open-source code (auditable)

### 5.3 Data Retention
- **Health data:** Retained indefinitely unless you delete it
- **Account data:** Retained until you delete your account
- **Backups:** Your responsibility (we recommend regular backups)

### 5.4 Data Deletion
You can delete your data at any time:
1. **Delete specific readings:** Use the API to delete individual readings
2. **Delete all data:** Stop the server and delete `undercurrent.db`
3. **Uninstall app:** Removes all local app data from your phone

## 6. Third-Party Integrations

### 6.1 Health Connect (Google)
- **Purpose:** Sync HRV/RHR and sleep data from your Garmin watch
- **Data shared:** Heart rate, HRV, sleep duration/quality
- **Privacy:** See [Google Health Connect Privacy Policy](https://policies.google.com/privacy)
- **Your control:** You can revoke permissions at any time in Health Connect settings

### 6.2 Garmin Health API (Future)
- **Purpose:** Access HRV data directly from Garmin
- **Data shared:** HRV, heart rate, sleep, stress, Body Battery
- **Privacy:** See [Garmin Privacy Policy](https://www.garmin.com/privacy/)
- **Your control:** OAuth authorization - you control what data Garmin shares
- **Revocation:** Revoke access anytime in Garmin Connect settings

## 7. GDPR Compliance (EU Users)

### 7.1 Legal Basis for Processing
- **Consent:** You explicitly consent by creating an account and granting Health Connect permissions
- **Legitimate Interest:** Managing your ME/CFS condition is a legitimate health interest

### 7.2 Your Rights Under GDPR
1. **Right to Access:** View all your data via the API (`GET /api/hrv/{user_id}/readings`)
2. **Right to Rectification:** Correct inaccurate data (contact us or use API)
3. **Right to Erasure (Right to be Forgotten):** Delete your account and all data
4. **Right to Data Portability:** Export your data in JSON format via API
5. **Right to Restrict Processing:** Stop calculations (pause the app)
6. **Right to Object:** Object to specific processing (contact us)
7. **Right to Withdraw Consent:** Revoke Health Connect permissions anytime

### 7.3 Data Portability
Export your data:
```bash
# Export all HRV readings
curl http://localhost:4777/api/hrv/1/readings?limit=1000 > my_hrv_data.json

# Export all energy budget scores
curl http://localhost:4777/api/energy-budget/1/readiness?limit=1000 > my_scores.json

# Export baseline
curl http://localhost:4777/api/energy-budget/1/baseline > my_baseline.json
```

### 7.4 Data Protection Officer
For small-scale operations (self-hosted), a DPO is not required. For questions, contact: [Your Email]

## 8. Children's Privacy

UnderCurrent is not intended for use by children under 16. We do not knowingly collect data from children. If you are under 16, please do not use this app without parental consent.

## 9. International Data Transfers

**For self-hosted instances:** Your data never leaves your local network. No international transfers occur.

**For cloud-hosted instances (future):** We will update this policy to specify data storage locations and safeguards (e.g., AWS region selection, Standard Contractual Clauses).

## 10. Security Breach Notification

In the unlikely event of a data breach:
- **Self-hosted:** You are responsible for securing your server
- **Cloud-hosted (future):** We will notify affected users within 72 hours per GDPR requirements

## 11. Cookies and Tracking

**We do not use:**
- ❌ Cookies (except session cookies if implemented)
- ❌ Analytics tracking
- ❌ Advertising trackers
- ❌ Social media pixels
- ❌ Fingerprinting

## 12. Research Use

**We do NOT use your data for research.** This app is for your personal health management only.

If we ever want to conduct research, we will:
1. Seek explicit opt-in consent
2. Anonymize all data
3. Submit to ethics board review
4. Publish results openly

## 13. Changes to This Policy

We will notify you of any material changes:
- Update the "Last Updated" date
- Notify via app update notes
- Email notification (if you provided email)

## 14. Open Source Transparency

UnderCurrent is open source:
- **Code:** https://github.com/bioluminesceme/UnderCurrent
- **License:** [Your chosen license]
- **Auditable:** Anyone can review the code to verify these privacy claims

## 15. Contact Us

For privacy questions or concerns:
- **Email:** [Your Email]
- **GitHub Issues:** https://github.com/bioluminesceme/UnderCurrent/issues

## 16. Governing Law

This Privacy Policy is governed by:
- **GDPR** (if you're in the EU)
- **HIPAA** does NOT apply (we are not a covered entity)
- **Local laws** in your jurisdiction

## 17. Medical Disclaimer

**UnderCurrent is NOT a medical device.** It is a wellness tool for personal health tracking. Do not use it to diagnose or treat medical conditions. Always consult your doctor.

## 18. Warranty and Liability

UnderCurrent is provided "as is" without warranty. We are not liable for:
- Data loss (backup your data!)
- Incorrect calculations
- Medical decisions based on app output
- Server security (your responsibility for self-hosted instances)

---

## Summary (Plain English)

✅ **Your data stays local** - no cloud servers
✅ **No tracking or ads** - we don't monetize your data
✅ **Open source** - anyone can audit the code
✅ **You control your data** - export or delete anytime
✅ **GDPR compliant** - all rights respected
✅ **Security first** - bcrypt passwords, local-only access

**Questions?** Contact us at [Your Email]

---

**By using UnderCurrent, you agree to this Privacy Policy.**
