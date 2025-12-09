"""
Setup test data for the CFS-HRV Monitor app.
This script creates:
1. A demo user (if not exists)
2. Multiple HRV readings over 7 days
3. A baseline calculation
4. An energy budget score

Run this script before using the app for the first time.
"""
import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:4777/api"
USER_ID = 1

def create_demo_user():
    """Create demo user if not exists"""
    print("Checking if demo user exists...")
    response = requests.get(f"{BASE_URL}/users/{USER_ID}")

    if response.status_code == 404:
        print("Creating demo user...")
        response = requests.post(
            f"{BASE_URL}/users/",
            json={
                "email": "demo@example.com",
                "password": "demo123"
            }
        )
        if response.status_code == 201:
            print(f"[OK] Created user: {response.json()['email']}")
        else:
            print(f"[ERROR] Failed to create user: {response.text}")
            return False
    else:
        print(f"[OK] User already exists: {response.json()['email']}")

    return True

def generate_rr_intervals(mean_hr=65, rmssd=45, count=300):
    """Generate realistic RR intervals"""
    mean_rri = 60000 / mean_hr  # Convert HR to RR interval
    intervals = [mean_rri]

    for i in range(1, count):
        # Generate successive difference with target RMSSD
        diff = random.gauss(0, rmssd / (2 ** 0.5))
        next_rri = intervals[-1] + diff
        # Keep within physiological range
        next_rri = max(300, min(2000, next_rri))
        intervals.append(next_rri)

    return intervals

def create_hrv_readings():
    """Create 7 days of HRV readings with varying quality"""
    print("\nCreating HRV readings for 7 days...")

    readings = []
    base_date = datetime.now() - timedelta(days=7)

    for day in range(7):
        # Vary HRV parameters to simulate real data
        mean_hr = random.uniform(60, 70)
        rmssd = random.uniform(40, 55)
        sleep_hours = random.uniform(6.5, 8.5)
        sleep_quality = random.uniform(75, 95)

        date = base_date + timedelta(days=day)

        rr_intervals = generate_rr_intervals(mean_hr, rmssd)

        response = requests.post(
            f"{BASE_URL}/hrv/{USER_ID}/readings",
            json={
                "rr_intervals": rr_intervals,
                "recorded_at": date.isoformat(),
                "sleep_duration": sleep_hours,
                "sleep_quality": sleep_quality
            }
        )

        if response.status_code == 201:
            reading = response.json()
            readings.append(reading)
            print(f"[OK] Day {day+1}: Reading ID {reading['id']} (HR: {mean_hr:.1f} bpm, RMSSD: {rmssd:.1f} ms)")
        else:
            print(f"[ERROR] Day {day+1}: Failed - {response.text}")

    return readings

def calculate_baseline():
    """Calculate baseline from the readings"""
    print("\nCalculating baseline...")

    response = requests.post(f"{BASE_URL}/energy-budget/{USER_ID}/baseline")

    if response.status_code == 200:
        baseline = response.json()
        print(f"[OK] Baseline calculated:")
        print(f"  - Days: {baseline['days_count']}")
        print(f"  - Mean RMSSD: {baseline['mean_rmssd']:.2f} ms")
        print(f"  - Mean HR: {baseline.get('mean_hr', 'N/A')} bpm")
        return baseline
    else:
        print(f"[ERROR] Failed to calculate baseline: {response.text}")
        return None

def calculate_energy_budget(reading_id):
    """Calculate energy budget for latest reading"""
    print(f"\nCalculating energy budget for reading {reading_id}...")

    response = requests.post(f"{BASE_URL}/energy-budget/{USER_ID}/readiness/{reading_id}")

    if response.status_code == 200:
        score = response.json()
        print(f"[OK] Energy Budget: {score['energy_budget']:.1f}")
        print(f"  - HRV Score: {score['hrv_score']:.1f}")
        print(f"  - RHR Score: {score['rhr_score']:.1f}")
        print(f"  - Sleep Score: {score['sleep_score']:.1f}")
        print(f"  - PEM Risk: {score['pem_risk_level']}")
        print(f"  - Recommendation: {score['activity_recommendation']}")
        return score
    else:
        print(f"[ERROR] Failed to calculate energy budget: {response.text}")
        return None

def main():
    print("=" * 60)
    print("UnderCurrent - Test Data Setup")
    print("=" * 60)

    # Step 1: Create user
    if not create_demo_user():
        return

    # Step 2: Create HRV readings
    readings = create_hrv_readings()
    if not readings:
        print("\n[ERROR] No readings created. Exiting.")
        return

    # Step 3: Calculate baseline
    baseline = calculate_baseline()
    if not baseline:
        print("\n[ERROR] Could not calculate baseline. Exiting.")
        return

    # Step 4: Calculate energy budget for latest reading
    latest_reading = readings[-1]
    score = calculate_energy_budget(latest_reading['id'])

    print("\n" + "=" * 60)
    if score:
        print("[SUCCESS] Test data setup complete!")
        print("\nYou can now use the Android app:")
        print("1. Open the app")
        print("2. Go to the 'Today' tab to see your Energy Budget")
        print("3. Or click 'Test Sync' to add more data")
    else:
        print("[ERROR] Test data setup incomplete")
    print("=" * 60)

if __name__ == "__main__":
    main()
