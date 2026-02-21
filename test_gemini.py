import requests

# PASTE YOUR API KEY HERE
API_KEY = "AIzaSyA4abVeeWUszf75QtfmCC-7SA4Z9CQLYeg"  # Replace with your actual key

# Test different API endpoints
test_prompt = "Say hello in isiZulu"

endpoints = [
    f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}",
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}",
    f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}",
]

for url in endpoints:
    print(f"\nTrying: {url}")
    try:
        data = {
            "contents": [{
                "parts": [{"text": test_prompt}]
            }]
        }
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ SUCCESS!")
            print(response.json()['candidates'][0]['content']['parts'][0]['text'])
            break
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")