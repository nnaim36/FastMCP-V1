from fastapi import FastAPI
from fastmcp import FastMCP
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

mcp = FastMCP(
    name="Database-Agent",
    host="127.0.0.1",
    port=8005
)

#connecting to mongo
client = MongoClient(os.getenv("MONGO_URI","mongodb://localhost:27017/"))
db = client["restaurantDB"]

locations_col = db["locations"]
menus_col = db["menus"]

googleMapsAPIKey = os.getenv("GOOGLE_MAPS_API_KEY")

@mcp.tool
def store_restaurants(location_data:dict) ->str:
    """
    Stores location and the resturants that are 1 miles away

    """

    location = location_data.get("location")
    restaurants = location_data.get("restaurants", [])
    user_location = location_data.get("user_location", {})

    if not location or not restaurants:
        return "Missing location or restaurant data."

    # Add or update menu_last_updated if not already set
    for r in restaurants:
        r["menu_last_updated"] = r.get("menu_last_updated", datetime.utcnow().isoformat() + "Z")

    locations_col.update_one(
        {"location": location},
        {"$set": {
            "restaurants": restaurants,
            "user_location": user_location
        }},
        upsert=True
    )
    return f"Stored restaurants for location: {location}"

@mcp.tool
def get_restaurants(location: str) -> list:
    result = locations_col.find_one({"location": location})
    return result.get("restaurants", []) if result else []

# Store menu data for a specific restaurant
@mcp.tool
def store_menu(menu_data: dict) -> str:
    restaurant = menu_data.get("restaurant")
    website = menu_data.get("website")
    location = menu_data.get("location")
    menu_items = menu_data.get("menu_items", [])

    if not restaurant or not menu_items:
        return "Missing restaurant or menu data."

    now = datetime.utcnow().isoformat() + "Z"

    menus_col.update_one(
        {"restaurant": restaurant, "website": website},
        {"$set": {
            "menu_items": menu_items,
            "location": location,
            "menu_last_updated": now
        }},
        upsert=True
    )
    return f"Stored menu for: {restaurant}"

# Retrieve menu and check freshness
@mcp.tool
def get_menu(restaurant: str) -> dict:
    result = menus_col.find_one({"restaurant": restaurant})

    if not result:
        return {"status": "NOT_FOUND", "menu_items": [], "last_updated": None}

    last_updated = result.get("menu_last_updated")
    if not last_updated:
        return {"status": "OUTDATED", "menu_items": result.get("menu_items", []), "last_updated": None}

    try:
        last_updated_dt = datetime.fromisoformat(last_updated.replace("Z", ""))
        if datetime.utcnow() - last_updated_dt > timedelta(days=60):
            return {
                "status": "OUTDATED",
                "menu_items": result.get("menu_items", []),
                "last_updated": last_updated
            }
    except Exception:
        return {
            "status": "OUTDATED",
            "menu_items": result.get("menu_items", []),
            "last_updated": last_updated
        }

    return {
        "status": "OK",
        "menu_items": result.get("menu_items", []),
        "last_updated": last_updated
    }

if __name__ == "__main__":
    mcp.run()