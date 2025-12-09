"""Create a demo user for testing"""
import requests
import urllib3

# Disable SSL warnings for self-signed certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

response = requests.post(
    "https://localhost:4777/api/users/",
    json={
        "email": "demo@example.com",
        "password": "demo123"
    },
    verify=False
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 201:
    user = response.json()
    print(f"\nSuccess! Created user ID: {user['id']}")
elif response.status_code == 400:
    print("\nUser already exists!")
else:
    print(f"\nError: {response.status_code}")
