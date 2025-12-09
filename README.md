# CFS-HRV Monitor

A research-backed Heart Rate Variability monitoring system for ME/CFS (Myalgic Encephalomyelitis/Chronic Fatigue Syndrome) management.

## Overview

This application calculates HRV metrics and readiness scores based on peer-reviewed research specific to ME/CFS patients, helping users track their recovery status and manage Post-Exertional Malaise (PEM) risk.

## Research Foundation

Based on validated studies:
- **Burton et al. (2010)**: HRV predicts sleep quality in CFS
- **Boneva et al. (2007)**: Higher heart rate and reduced HRV persist during sleep in CFS
- **Meeus et al. (2013)**: Systematic review of HRV in FM/CFS patients

## Key Features

### 1. HRV Calculations
- **Time domain metrics**: RMSSD, SDNN, PNN50
- **Frequency domain metrics**: VLF, LF, HF, Total Power, LF/HF ratio
- **Data quality checks**: Artifact detection and validation

### 2. Baseline Tracking
- 28-day rolling baseline with z-score normalization
- Individual baseline calculation (not population averages)
- Automatic baseline updates

### 3. Readiness Score
Research-weighted components:
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

The API will be available at `http://localhost:4777`

3. View API documentation:
- Swagger UI: `http://localhost:4777/docs`
- ReDoc: `http://localhost:4777/redoc`

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

Research and educational use.

## Contributing

This is a prototype implementation based on peer-reviewed research. Contributions should reference published studies and maintain scientific rigor.
