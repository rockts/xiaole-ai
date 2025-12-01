import requests
import json

base_url = "http://localhost:8000"

# 1. Login
login_url = f"{base_url}/token"
login_data = {
    "username": "admin",
    "password": "admin123"
}
print(f"Logging in to {login_url}...")
try:
    login_res = requests.post(login_url, data=login_data)
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        exit(1)
    token = login_res.json()["access_token"]
    print("Login successful.")
except Exception as e:
    print(f"Login exception: {e}")
    exit(1)

# 2. Chat Stream
url = f"{base_url}/api/chat/stream"
params = {
    "prompt": "你好",
    "user_id": "admin"
}
headers = {
    "Authorization": f"Bearer {token}"
}

print(f"Sending request to {url}...")
try:
    response = requests.post(url, params=params, headers=headers, stream=True)
    print(f"Response status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error content: {response.text}")
    else:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(decoded_line)
except Exception as e:
    print(f"Exception: {e}")
