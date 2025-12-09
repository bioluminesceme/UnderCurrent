"""Create a demo user for testing"""
import requests

response = requests.post(
    "http://localhost:4777/api/users/",
    json={
        "email": "demo@example.com",
        "password": "demo123"
    }
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
