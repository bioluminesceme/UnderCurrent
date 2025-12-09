# UnderCurrent

An experimental energy monitoring tool for personal ME/CFS management.

## ⚠️ IMPORTANT DISCLAIMERS

**This software is in early development and NOT production-ready:**
- Under active development with frequent breaking changes
- Not suitable for clinical use or medical decision-making
- Self-hosted only - no cloud version available or planned
- Use entirely at your own risk

**Medical Disclaimer:**
- This is NOT a medical device
- Do not use for diagnosis or treatment decisions
- Always consult healthcare professionals for medical advice
- The developers assume no liability for any health outcomes

## Overview

UnderCurrent is an experimental tool that calculates HRV/RHR metrics and energy budget scores. While informed by research on ME/CFS, this is a personal monitoring project, not a validated medical tool.

## Research Background

Implementation informed by published research:
- Burton et al. (2010): HRV predicts sleep quality in CFS
- Boneva et al. (2007): Higher heart rate and reduced HRV persist during sleep in CFS
- Meeus et al. (2013): Systematic review of HRV in FM/CFS patients

Note: While based on research, this implementation is experimental and unvalidated.

## Key Features

### 1. HRV Calculations
- **Time domain metrics**: RMSSD, SDNN, PNN50
- **Frequency domain metrics**: VLF, LF, HF, Total Power, LF/HF ratio
- **Data quality checks**: Artifact detection and validation

### 2. Baseline Tracking
- 28-day rolling baseline with z-score normalization
- Individual baseline calculation (not population averages)
- Automatic baseline updates

### 3. Energy Budget Score
Experimental weighting of components:
- 40% HRV (RMSSD + HF power)
- 30% RHR (resting heart rate)
- 20% Sleep quality
- 10% Stress level

### 4. PEM Risk Assessment
Monitors for warning signs:
- 3+ consecutive days of HRV below -1 SD
- Heart rate elevated >10% above baseline
- RMSSD drop >25% from baseline

## Installation

### Requirements
- Python 3.8+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

1. Install dependencies:
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

2. Run the server:
```bash
# Using uv
uv run python run_server.py

# Or if installed with pip
python run_server.py
```

The API will be available at `https://localhost:4777` (HTTPS with self-signed certificate)

3. View API documentation:
- Swagger UI: `https://localhost:4777/docs`
- ReDoc: `https://localhost:4777/redoc`

Note: Your browser will warn about the self-signed certificate - this is expected for local development.

## Testing

Run the test suite to verify functionality:

```bash
# Using uv
uv run python test_api.py

# Or if installed with pip
python test_api.py
```

This will:
1. Create a test user
2. Submit HRV readings
3. Build a baseline
4. Calculate readiness scores
5. Generate trend data

## API Endpoints

### Users
- `POST /api/users/` - Create new user
- `GET /api/users/{user_id}` - Get user details

### HRV Readings
- `POST /api/hrv/{user_id}/readings` - Submit RR intervals for HRV calculation
- `GET /api/hrv/{user_id}/readings` - Get recent readings
- `GET /api/hrv/{user_id}/readings/{reading_id}` - Get specific reading

### Readiness & Baseline
- `POST /api/readiness/{user_id}/baseline` - Calculate 28-day baseline
- `GET /api/readiness/{user_id}/baseline` - Get active baseline
- `POST /api/readiness/{user_id}/readiness/{reading_id}` - Calculate readiness score
- `GET /api/readiness/{user_id}/readiness` - Get recent readiness scores
- `GET /api/readiness/{user_id}/readiness/trend/{days}` - Get trend data
- `GET /api/readiness/{user_id}/interpretation/{rmssd}/{hr}` - Get HRV interpretation

## Database Schema

### Tables
- **users**: User accounts and profile information
- **hrv_readings**: Time and frequency domain HRV metrics
- **baselines**: 28-day rolling baselines with z-score parameters
- **readiness_scores**: Daily readiness scores with PEM risk assessment

## Clinical Thresholds

### Population References (from Boneva et al. 2007)

**Healthy controls (during sleep):**
- RMSSD: ~66.6 ms
- Heart rate: ~64.8 bpm

**CFS patients (during sleep):**
- RMSSD: ~51.1 ms
- Heart rate: ~71.4 bpm

### Warning Thresholds

**Critical HRV:**
- RMSSD < 30 ms: Similar to severe CFS cases
- RMSSD < 50 ms: Within CFS patient range

**Elevated Heart Rate:**
- HR > 75 bpm: Above CFS patient mean
- HR > 70 bpm: Within CFS patient range

**Z-Score Interpretation:**
- z > 0.5: Excellent recovery
- z > 0: Good recovery
- z > -0.5: Fair (monitor)
- z > -1.0: Low (reduce activity)
- z > -1.5: Warning (rest recommended)
- z ≤ -1.5: Critical (prioritize rest)

## Activity Recommendations

Based on readiness score and PEM risk:

- **Normal activity**: Readiness ≥70, low PEM risk
- **Light activity**: Readiness 50-70
- **Reduced activity**: Readiness 30-50
- **Rest**: Readiness <30 or high PEM risk

## Project Structure

```
UnderCurrentAppPaxum/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── hrv_calculator.py    # HRV metric calculations
│   ├── baseline_tracker.py  # Baseline tracking and z-scores
│   ├── readiness_calculator.py  # Readiness score algorithm
│   └── api/
│       ├── users.py         # User endpoints
│       ├── hrv.py           # HRV reading endpoints
│       └── readiness.py     # Readiness/baseline endpoints
├── research/
│   ├── HRV_Formulas_and_Calculations.md  # Complete formula reference
│   └── RESEARCH_SUMMARY.md                # Implementation guide
├── requirements.txt
├── run_server.py
├── test_api.py
└── README.md
```

## Future Enhancements (Phase 2+)

- [ ] Garmin device integration
- [ ] Frontend web/mobile app
- [ ] Data visualization dashboard
- [ ] Export reports (PDF/CSV)
- [ ] Multi-user authentication (JWT)
- [ ] Activity tracking integration
- [ ] Symptom logging
- [ ] PEM prediction model

## References

1. Burton, A. R., et al. (2010). Reduced heart rate variability predicts poor sleep quality in chronic fatigue syndrome. *Experimental Brain Research*, 204:71-78.

2. Boneva, R. S., et al. (2007). Higher heart rate and reduced heart rate variability persist during sleep in chronic fatigue syndrome. *Autonomic Neuroscience*, 137:94-101.

3. Meeus, M., et al. (2013). Heart rate variability in patients with fibromyalgia and chronic fatigue syndrome. *Seminars in Arthritis and Rheumatism*, 43(2):279-287.

## License

MIT License - Open Source

Copyright (c) 2024 UnderCurrent Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

This is an experimental implementation. Contributions are welcome, but remember this is not a validated medical tool. Please include references to research where applicable.
