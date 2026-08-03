# Fetch data from API with retry
import requests, time

def safe_api_call(url, params, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API failed (try {attempt+1}): {e}")
            time.sleep(5)
    return None
