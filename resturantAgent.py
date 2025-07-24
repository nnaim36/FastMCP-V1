from datetime import datetime, timedelta
import requests
from fastmcp import FastMCP
import os
import re
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(
    name="Resturant-Agent",
    host="127.0.0.1",
    port=8003
)

googleMapsAPIKey = os.getenv("GOOGLE_MAPS_API_KEY")

def calc_resturant_distance(user_lat, user_lon, rest_lat, rest_lon):
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
        return "unknown"

def fetch_place_website(place_id: str, api_key: str) -> str:
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "website",
        "key": api_key
    }
    try:
        response = requests.get(url, params=params)
        return response.json().get("result", {}).get("website")
    except:
        return None

@mcp.tool
def find_local_resturants_google(lat: float, lon: float, radius: int = 1000, budget: int = 17, location: str = "") -> list:
    """
    Checks DB for fresh restaurant data, else fetches new results from Google Maps and stores them.
    """

    # Step 1: Query Database Agent for existing data
    try:
        db_response = requests.post(
            "http://127.0.0.1:8004/tools/get_restaurants",
            json={"location": location},
            timeout=10
        )
        print(f"[INFO] Stored restaurant data to DB: {store_response.text}")
        print("[DEBUG] DB POST Status:", store_response.status_code)
        print("[DEBUG] DB Response Body:", store_response.text)
        if db_response.status_code == 200:
            db_data = db_response.json()
            if db_data:
                last_updated_str = db_data[0].get("menu_last_updated")
                if last_updated_str:
                    last_updated = datetime.fromisoformat(last_updated_str.replace("Z", ""))
                    if datetime.utcnow() - last_updated < timedelta(days=60):
                        print("[INFO] Returning cached restaurant data")
                        return db_data
    except Exception as e:
        print(f"[WARN] Failed DB fetch: {e}")

    # Step 2: Perform new search
    maps_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    maps_params = {
        "location": f"{lat},{lon}",
        "radius": radius,
        "type": "restaurant",
        "key": googleMapsAPIKey
    }

    try:
        response = requests.get(maps_url, params=maps_params)
        response.raise_for_status()
        results = response.json().get("results", [])
        enriched = []

        for r in results[:10]:
            place_id = r.get("place_id")
            geo = r.get("geometry", {}).get("location", {})
            website = fetch_place_website(place_id, googleMapsAPIKey) if place_id else None
            if not geo:
                continue

            distance = calc_resturant_distance(lat, lon, geo["lat"], geo["lng"])
            location_name = r.get("vicinity", "").split(",")[-1].strip()

            menu_data = {"menu_items": [], "best_combinations": []}
            if website:
                try:
                    menu_resp = requests.post(
                        "http://127.0.0.1:8004/tools/scrape_menu",  # <- adjust if on another host
                        json={"homepages": [website], "budget": budget},
                        timeout=20
                    )
                    if menu_resp.status_code == 200:
                        menu_data = menu_resp.json()
                except Exception as e:
                    print(f"[ERROR] Menu scrape failed: {e}")

            enriched.append({
                "name": r.get("name"),
                "address": r.get("vicinity"),
                "rating": r.get("rating"),
                "distance": distance,
                "website": website,
                "menu_last_updated": datetime.utcnow().isoformat() + "Z"
            })

        # Step 3: Store new data to Database Agent
        try:
            store_payload = {
                "location": location,
                "user_location": {"lat": lat, "lon": lon},
                "restaurants": enriched
            }
            store_response = requests.post(
                "http://127.0.0.1:8004/tools/store_restaurants",
                json=store_payload,
                timeout=10
            )
            print(f"[INFO] Stored restaurant data to DB: {store_response.text}")
        except Exception as e:
            print(f"[ERROR] Failed to store restaurant data: {e}")

        return enriched

    except Exception as e:
        print(f"[ERROR] Google Maps API failed: {e}")
        return []

    #a = ["test4", "test5"]
    #return a

'''
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
'''


if __name__ == "__main__":
    mcp.run()

'''
if __name__ == "__main__":
    result = find_local_resturants_google(
        lat=42.4184,
        lon=-71.1097,
        radius=1000,
        budget=17,
        location="66 Bow Street, Medford, MA"
    )
    print("[RESULT]", result)
'''