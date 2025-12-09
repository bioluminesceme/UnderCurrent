# Privacy Policy for UnderCurrent

**Last Updated:** December 9, 2025

---

## IMPORTANT: Two Deployment Models

UnderCurrent can be used in two ways. Please read the section that applies to you:

### 📱 **Self-Hosted (Current Version)**
You run your own server on your computer at home. Your data never leaves your local network.
👉 **See: [Section A - Self-Hosted Privacy Policy](#section-a-self-hosted-privacy-policy)**

### ☁️ **Cloud-Hosted (Maybe Future - VERY UNCERTAIN)**
We *might* host a server someday. This is a big maybe. We're focusing on local-only for now.
👉 **See: [Section B - Cloud-Hosted Privacy Policy](#section-b-cloud-hosted-privacy-policy)**

---

# Section A: Self-Hosted Privacy Policy

**Current Version - This is how the app works TODAY**

## 1. Introduction

When you self-host UnderCurrent, **you are in complete control** of your data. The app communicates with a server that **you run on your own computer** at home.

**TL;DR:** Your health data stays on your device and your local server. We can't see it. You control it. It never goes to the internet.

## 2. What Data is Collected

### 2.1 Health Data (Stored on YOUR server)
- **Heart Rate Variability (HRV)** or **Resting Heart Rate (RHR)**
- Sleep duration and quality scores
- Heart rate measurements
- Activity levels
- Calculated metrics (z-scores, energy budget scores, PEM risk assessments)

### 2.2 Account Data (Stored on YOUR server)
- Email address (for login only)
- Hashed password (bcrypt, never plain text)
- Account creation timestamp

### 2.3 Data We Do NOT Collect
- ❌ Location data
- ❌ Contact lists
- ❌ Analytics or tracking
- ❌ Advertising identifiers
- ❌ Any data sent to third-party servers

## 3. Where is Your Data Stored?

**Location:** On your computer, in a SQLite database file
**Path:** `F:\UnderCurrentAppPaxum\backend\undercurrent.db` (or wherever you installed it)
**Network:** Local network only (127.0.0.1 or 192.168.x.x)
**Internet:** Your data does NOT go to the internet

## 4. Who Can Access Your Data?

- ✅ **You** - full access
- ❌ **UnderCurrent developers** - we have NO access
- ❌ **Third parties** - no third parties involved 

## 5. Data Security (Self-Hosted)

**Your Responsibility:**
- Keep your local network secure (use WPA3 Wi-Fi)

**Built-in Security:**
- ✅ Passwords hashed with bcrypt
- ✅ No plain-text password storage
- ✅ No third-party analytics SDKs
- ✅ Open-source code  

**Network Security:**
- ✅  Uses HTTPS over local network (cleartext)
- ✅ Local network only (not exposed to internet)


## 6. Data Retention (Self-Hosted)

- **Retention period:** Forever, until you delete it
- **Your control:** You can delete the database file anytime
- **Backups:** Your responsibility, we do not have access.

## 7. Third-Party Integrations

### Health Connect (Google)
- **Purpose:** Sync HRV/RHR and sleep data from your Garmin watch
- **Data flow:** Garmin → Health Connect → UnderCurrent → Your local server
- **Privacy:** See [Google Health Connect Privacy Policy](https://policies.google.com/privacy)
- **Your control:** Revoke permissions anytime in Health Connect settings

### Garmin Health API (Future I've applied for developer access)
- **Purpose:** Access HRV data directly from Garmin servers
- **Data flow:** Garmin servers → UnderCurrent app → Your local server so your app can read it.
- **Privacy:** See [Garmin Privacy Policy](https://www.garmin.com/privacy/)
- **Your control:** OAuth - you authorize what data Garmin shares

## 8. GDPR Rights (Self-Hosted)

Since you control your own data:

1. **Right to Access:** You have full access via the API
2. **Right to Erasure:** Delete the database file
3. **Right to Portability:** Export data via API in JSON format
4. **Right to Rectification:** Edit the database directly
5. **Right to Restrict Processing:** Stop the server

**No Data Protection Officer required** - you are your own DPO.

---

# Section B: Cloud-Hosted Privacy Policy

**SPECULATIVE - VERY UNCERTAIN - FOCUS IS LOCAL-ONLY**

## 1. Introduction (Cloud-Hosted)

**This section describes how UnderCurrent MIGHT work IF we ever launch a cloud-hosted version.** This is purely speculative. We are currently focused on making the self-hosted version work well. A cloud version is a distant "maybe."

IF we ever build a cloud-hosted version, we will host the server so you can use the app from anywhere without running your own server.

**TL;DR:** We will encrypt your data. We won't sell it. We won't look at it. You can delete it anytime. Free to use.

## 2. What Data We Will Collect (Cloud-Hosted)

Same health data as self-hosted version, but stored on our servers instead of yours.

### 2.1 Health Data (Stored on OUR server)
- Heart Rate Variability (HRV) / Resting Heart Rate (RHR)
- Sleep duration and quality
- Heart rate measurements
- Activity levels
- Calculated metrics

### 2.2 Account Data (Stored on OUR server)
- Email address (for login and password reset)
- Hashed password (bcrypt with unique salt per user)
- Account creation and last login timestamp
- User ID (anonymized UUID)

### 2.3 Data We Will NOT Collect
- ❌ Real name (unless you put it in your email)
- ❌ Phone number
- ❌ Location data
- ❌ Payment information (free service)
- ❌ Advertising identifiers
- ❌ Analytics or tracking (except anonymous error reports)

## 3. Where Will Your Data Be Stored? (Cloud-Hosted)

**Hosting Provider:** [TBD - likely AWS, Google Cloud, or Hetzner]
**Data Center Location:** [TBD - will be disclosed before launch]
**Database:** PostgreSQL with encryption at rest
**Backups:** Encrypted backups with unique encryption keys

## 4. How We Will Protect Your Data (Cloud-Hosted)

### 4.1 Encryption

**In Transit:**
- ✅ TLS 1.3 encryption (HTTPS only)
- ✅ Certificate pinning (prevents man-in-the-middle attacks)
- ✅ No HTTP fallback

**At Rest:**
- ✅ Database encryption at rest (AES-256)
- ✅ Each user's data encrypted with unique salt
- ✅ Password hashes use bcrypt with per-user salt

**Anonymization:**
- ✅ User ID is a UUID (not sequential)
- ✅ No IP address logging
- ✅ No personally identifiable information required

### 4.2 Access Control

**Who Can Access Your Data:**
- ✅ **You** - via app or API
- ⚠️ **System administrators** - for maintenance only (see below)
- ❌ **Other users** - cannot see your data
- ❌ **Advertisers** - we have no advertising
- ❌ **Third parties** - no data sharing

**Admin Access Policy:**
- Admins CAN access the database for maintenance
- Admins CANNOT decrypt individual user data (encrypted at application level)
- Admins are logged and monitored
- All admin access requires 2FA

### 4.3 Data Retention (Cloud-Hosted)

**Active Users:**
- Health data: Retained as long as your account is active
- Account data: Retained as long as your account is active

**Inactive Users:**
- **After 2 years of inactivity:** We will email you a warning
- **After 3 years of inactivity:** Account and data will be deleted

**Deleted Accounts:**
- All data deleted within 30 days
- Backups purged after 90 days
- No data retained after deletion

**User-Initiated Deletion:**
- ✅ Immediate deletion from production database
- ✅ Backup purge within 90 days
- ✅ Confirmation email sent

## 5. Data Sharing (Cloud-Hosted)

**We will NEVER:**
- ❌ Sell your data
- ❌ Share data with advertisers
- ❌ Use data for marketing
- ❌ Train AI models on your data (without explicit opt-in consent)

**We MAY share anonymized, aggregated data:**
- ✅ For medical research (only with your opt-in consent)
- ✅ Anonymized and aggregated (no individual identification possible)
- ✅ Published openly (e.g., "Average energy budget for 1000 ME/CFS patients")

## 6. International Data Transfers (Cloud-Hosted)

**EU Users:**
- Data will be stored in EU data centers (GDPR compliant)
- No transfers outside EU without Standard Contractual Clauses

**Non-EU Users:**
- Data will be stored in nearest regional data center
- Transfers comply with local data protection laws

## 7. GDPR Rights (Cloud-Hosted)

You will have full GDPR rights:

1. **Right to Access:** Export all your data in JSON format
2. **Right to Rectification:** Edit or correct your data via app
3. **Right to Erasure (Right to be Forgotten):** Delete account and all data
4. **Right to Data Portability:** Download all data in machine-readable format
5. **Right to Restrict Processing:** Temporarily pause calculations
6. **Right to Object:** Object to specific data processing
7. **Right to Withdraw Consent:** Revoke permissions anytime

**Data Protection Officer:** [Email TBD]

## 8. Security Breach Notification (Cloud-Hosted)

In the event of a data breach:
- We will notify affected users within **72 hours** (GDPR requirement)
- We will notify relevant data protection authorities
- We will provide details of the breach and mitigation steps
- We will offer free credit monitoring if applicable

## 9. Business Model (Cloud-Hosted)

**Free Tier:**
- ✅ Unlimited data storage
- ✅ All features included
- ✅ No ads, no tracking

**How We Pay For It:**
- Donations (optional)
- Grants from ME/CFS organizations
- Sponsorships (listed transparently, no data access)

**We will NEVER:**
- ❌ Charge for basic features
- ❌ Sell premium plans that exploit chronically ill users
- ❌ Monetize your health data

## 10. Cloud-Hosted Roadmap

**Current Priority:** Get self-hosted version working perfectly first.

**Cloud-Hosted Status:** Distant maybe. Not planned for at least 12+ months. May never happen.

**IF we ever do it, we will:**
- ✅ Complete security audit by third party
- ✅ Implement end-to-end encryption
- ✅ Set up SOC 2 compliance
- ✅ Get legal review by privacy lawyer
- ✅ Publish transparency report
- ✅ Update this privacy policy with concrete details

**Current Focus:** Local-only, self-hosted, privacy-first.

---

# Universal Sections (Both Self-Hosted and Cloud-Hosted)

## Children's Privacy

UnderCurrent is not intended for children under 16. We do not knowingly collect data from children.

## Medical Disclaimer

**UnderCurrent is NOT a medical device.** Do not use it to diagnose or treat medical conditions. Always consult your doctor.

## Warranty and Liability

UnderCurrent is provided "as is" without warranty. We are not liable for:
- Data loss (always backup your data!)
- Incorrect calculations
- Medical decisions based on app output
- Security breaches (for self-hosted versions, you are responsible)

## Open Source Transparency

UnderCurrent is open source:
- **Code:** https://github.com/bioluminesceme/UnderCurrent
- **License:** [Your chosen license]
- **Auditable:** Anyone can review the code

## Changes to This Policy

We will notify you of changes:
- Update "Last Updated" date
- Notify via app update notes
- Email notification (for cloud-hosted users)

## Contact Us

**For Privacy Questions:**
- **GitHub Issues:** https://github.com/bioluminesceme/UnderCurrent/issues
- **Email:** [Your Email TBD]

## Governing Law

- **GDPR** (EU users)
- **CCPA** (California users, cloud-hosted only)
- **HIPAA** does NOT apply (we are not a covered entity)

---

## Summary Table

| Feature                  | Self-Hosted (Now)              | Cloud-Hosted (Future)                          |
| ------------------------ | ------------------------------ | ---------------------------------------------- |
| **Data Location**        | Your computer                  | Our servers                                    |
| **We Can See Your Data** | ❌ No                           | ⚠️ Encrypted, admin access for maintenance only |
| **Internet Required**    | ❌ Local network only           | ✅ Yes                                          |
| **Free**                 | ✅ Yes                          | ✅ Yes                                          |
| **Your Responsibility**  | Server security, backups       | Just use the app                               |
| **Data Encryption**      | Optional (recommend full-disk) | ✅ Always (TLS + AES-256)                       |
| **Data Retention**       | Forever (you control)          | Until account deletion or 3 years inactive     |
| **GDPR Compliant**       | ✅ You control your data        | ✅ Yes                                          |

---

**By using UnderCurrent, you agree to this Privacy Policy.**

**Questions? Open an issue on GitHub or contact us!**
