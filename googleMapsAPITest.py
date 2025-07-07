import requests
import os

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GOOGLE_MAPS_API_KEY")  # or hardcode: "your_key_here"

params = {
    "location": "42.4184,-71.1061",
    "radius": 1000,
    "type": "restaurant",
    "key": api_key
}

url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

response = requests.get(url, params=params)

print("Status:", response.status_code)
print("Response:", response.json())