from fastapi import FastAPI
from fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import itertools
import re
import os
import requests
from urllib.parse import unquote, urlparse, parse_qs
from dotenv import load_dotenv


load_dotenv()

mcp = FastMCP(
    name="Resturant-Agent",
    host="127.0.0.1",
    port=8003
)

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
googleMapsAPIKey = os.getenv("GOOGLE_MAPS_API_KEY")

def calc_resturant_distance(user_lat,user_lon,rest_lat,rest_lon):
    origin = f"{user_lat},{user_lon}"
    destination = f"{rest_lat},{rest_lon}"
    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?"
        f"origins={origin}&destinations={destination}&mode=walking"
        f"&units=imperial&key={googleMapsAPIKey}"
    )

    try:
        response = requests.get(url)
        data = response.json()
        return data["rows"][0]["elements"][0]["distance"]["text"]
    except:
        return "trouble calculating distance"                                                                                                                                                                                                          


def price_parse(_text:str)->float:
    match = re.search(r'\$?(\d+\.\d{2})', _text)
    return float(match.group(1)) if match else None

def fetch_place_website(place_id: str, api_key: str) -> str:
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "website",
        "key": api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json().get("result", {})
        return result.get("website")
    except Exception as e:
        print(f"[ERROR] Failed to fetch website for {place_id}: {e}")
        return None


@mcp.tool
def find_local_resturants_google(lat: float, lon: float, radius: int = 1000) -> list:
    """
    Find restaurants near a location using google maps legacy API using lat and lon
    """

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": radius,
        "type": "restaurant",
        "key": googleMapsAPIKey
    }

    try:
        response = requests.get(url, params=params)
        #print("[DEBUG] Status:", response.status_code)
        #print("[DEBUG] JSON:", response.json())
        response.raise_for_status()
        results = response.json().get("results", [])
        restaurants = []
        for r in results[:10]:  # limit to first 10 to stay under quota
            place_id = r.get("place_id")
            website = fetch_place_website(place_id, googleMapsAPIKey) if place_id else None

            restaurants.append({
                "name": r.get("name"),
                "address": r.get("vicinity"),
                "rating": r.get("rating"),
                "location": r.get("geometry", {}).get("location"),
                "place_id": place_id,
                "website": website
            })

        return restaurants

    except Exception as e:
        print(f"[ERROR] Google Maps API: {e}")
        return []

    #a = ["test4", "test5"]
    #return a

@mcp.tool
def scrape_menu(_urlsList:list, _budget:int) -> dict:
    """
    scapes the menus of resturants for food items and their prices.
    the output is the combinations options that are in the users budget.
    """

    menuItems = []

    for url in _urlsList:
        try:
            html = requests.get(url, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")
            texts = soup.stripped_strings
            for text in texts:
                price = price_parse(text)
                if price:
                    name = text.replace(f"${price}", "").strip()
                    if 0 < price <= _budget:
                        menuItems.append((name, price))
        except:
            continue

    # Generate combos
    combos = []
    for i in range(1, len(menuItems) + 1):
        for combo in itertools.combinations(menuItems, i):
            total = sum(item[1] for item in combo)
            if total <= _budget:
                combos.append((combo, round(total, 2)))

    combos.sort(key=lambda x: -x[1])
    return {
        "menu_items": menuItems,
        "best_combinations": combos[:10]
    }


if __name__ == "__main__":
    mcp.run()