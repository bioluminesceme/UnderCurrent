"""
Basic API tests to verify HRV calculations and readiness scoring.

Run after starting the server with: python run_server.py
"""
import requests
import urllib3
import numpy as np
from datetime import datetime

# Disable SSL warnings for self-signed certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:4777/api"

def generate_sample_rr_intervals(mean_hr=70, rmssd=50, num_intervals=300):
    """
    Generate synthetic RR intervals for testing.

    Args:
        mean_hr: Mean heart rate (bpm)
        rmssd: Target RMSSD (ms)
        num_intervals: Number of intervals to generate

    Returns:
        List of RR intervals in milliseconds
    """
    # Calculate mean RR interval from heart rate
    mean_rri = 60000 / mean_hr

    # Generate successive differences with target RMSSD
    successive_diffs = np.random.normal(0, rmssd / np.sqrt(2), num_intervals - 1)

    # Generate RR intervals
    rr_intervals = [mean_rri]
    for diff in successive_diffs:
        next_rri = rr_intervals[-1] + diff
        # Keep within physiological range (300-2000ms)
        next_rri = max(300, min(2000, next_rri))
        rr_intervals.append(next_rri)

    return rr_intervals

def test_create_user():
    """Test creating a new user"""
    print("\n=== Test 1: Create User ===")

    user_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "age": 35,
        "sex": "F",
        "bmi": 22.5
    }

    response = requests.post(f"{BASE_URL}/users/", json=user_data, verify=False)
    print(f"Status: {response.status_code}")

    if response.status_code in [200, 201]:
        user = response.json()
        print(f"Created user ID: {user['id']}")
        return user['id']
    else:
        print(f"Error: {response.text}")
        return None

def test_submit_hrv_reading(user_id):
    """Test submitting HRV data"""
    print("\n=== Test 2: Submit HRV Reading ===")

    # Generate sample data simulating CFS patient (low RMSSD, high HR)
    rr_intervals = generate_sample_rr_intervals(mean_hr=72, rmssd=45, num_intervals=300)

    hrv_data = {
        "rr_intervals": rr_intervals,
        "recorded_at": datetime.utcnow().isoformat(),
        "sleep_duration": 7.5,
        "sleep_quality": 65.0
    }

    response = requests.post(f"{BASE_URL}/hrv/{user_id}/readings", json=hrv_data, verify=False)
    print(f"Status: {response.status_code}")

    if response.status_code in [200, 201]:
        reading = response.json()
        print(f"Reading ID: {reading['id']}")
        print(f"RMSSD: {reading['rmssd']:.2f} ms")
        print(f"Mean HR: {reading['mean_hr']:.2f} bpm")
        print(f"Total Power: {reading['total_power']:.2f} ms²")
        print(f"LF/HF Ratio: {reading['lf_hf_ratio']:.2f}")
        return reading['id']
    else:
        print(f"Error: {response.text}")
        return None

def test_build_baseline(user_id):
    """Test building baseline after multiple readings"""
    print("\n=== Test 3: Build Baseline (10 days of data) ===")

    # Submit 10 days of readings
    reading_ids = []
    for day in range(10):
        # Simulate slight variation in HRV
        mean_hr = 71 + np.random.normal(0, 2)
        rmssd = 48 + np.random.normal(0, 5)

        rr_intervals = generate_sample_rr_intervals(mean_hr=mean_hr, rmssd=rmssd)

        recorded_at = datetime.utcnow().replace(hour=8, minute=0, second=0)
        recorded_at = recorded_at.replace(day=recorded_at.day - (10 - day))

        hrv_data = {
            "rr_intervals": rr_intervals,
            "recorded_at": recorded_at.isoformat(),
            "sleep_duration": 7.0 + np.random.normal(0, 0.5),
            "sleep_quality": 60.0 + np.random.normal(0, 10)
        }

        response = requests.post(f"{BASE_URL}/hrv/{user_id}/readings", json=hrv_data, verify=False)
        if response.status_code in [200, 201]:
            reading_ids.append(response.json()['id'])

    print(f"Created {len(reading_ids)} readings")

    # Calculate baseline
    response = requests.post(f"{BASE_URL}/readiness/{user_id}/baseline", verify=False)
    print(f"Baseline Status: {response.status_code}")

    if response.status_code in [200, 201]:
        baseline = response.json()
        print(f"Baseline Mean RMSSD: {baseline['mean_rmssd']:.2f} ms")
        print(f"Baseline Mean ln(RMSSD): {baseline['mean_ln_rmssd']:.3f}")
        print(f"Baseline SD ln(RMSSD): {baseline['sd_ln_rmssd']:.3f}")
        print(f"Baseline Mean HR: {baseline['mean_hr']:.2f} bpm")
        return reading_ids
    else:
        print(f"Error: {response.text}")
        return reading_ids

def test_calculate_readiness(user_id, reading_id):
    """Test calculating readiness score"""
    print("\n=== Test 4: Calculate Readiness Score ===")

    response = requests.post(f"{BASE_URL}/readiness/{user_id}/readiness/{reading_id}", verify=False)
    print(f"Status: {response.status_code}")

    if response.status_code in [200, 201]:
        score = response.json()
        print(f"Readiness Score: {score['readiness_score']:.1f}/100")
        print(f"HRV Score: {score['hrv_score']:.1f}/100 (z={score['hrv_zscore']:.2f})")
        print(f"RHR Score: {score['rhr_score']:.1f}/100 (z={score['rhr_zscore']:.2f})")
        print(f"Sleep Score: {score['sleep_score']:.1f}/100")
        print(f"Stress Score: {score['stress_score']:.1f}/100")
        print(f"PEM Risk: {score['pem_risk_level']}")
        print(f"Activity Recommendation: {score['activity_recommendation']}")
        return score
    else:
        print(f"Error: {response.text}")
        return None

def test_get_trend(user_id):
    """Test getting readiness trend"""
    print("\n=== Test 5: Get 7-Day Readiness Trend ===")

    response = requests.get(f"{BASE_URL}/readiness/{user_id}/readiness/trend/7", verify=False)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        trend = response.json()
        print(f"Trend data points: {len(trend)}")
        if trend:
            print("\nRecent scores:")
            for entry in trend[-3:]:
                print(f"  {entry['date'][:10]}: {entry['readiness_score']:.1f} ({entry['activity_recommendation']})")
    else:
        print(f"Error: {response.text}")

def run_all_tests():
    """Run complete test suite"""
    print("=" * 60)
    print("CFS-HRV Monitor API Test Suite")
    print("=" * 60)

    # Test 1: Create user
    user_id = test_create_user()
    if not user_id:
        print("\nFailed to create user. Exiting tests.")
        return

    # Test 2: Submit single reading
    reading_id = test_submit_hrv_reading(user_id)

    # Test 3: Build baseline with multiple readings
    reading_ids = test_build_baseline(user_id)

    # Test 4: Calculate readiness for latest reading
    if reading_ids:
        test_calculate_readiness(user_id, reading_ids[-1])

    # Test 5: Get trend
    test_get_trend(user_id)

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API server.")
        print("Please start the server first with: python run_server.py")
    except Exception as e:
        print(f"\nError during tests: {e}")
        import traceback
        traceback.print_exc()
