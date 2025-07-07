from fastapi import FastAPI
from fastmcp import FastMCP
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(
    name="Database-Agent"
    host="127.0.0.1",
    port=8004
)

#connecting to mongo
client = MongoClient(os.getenv("MONGO_URI","mongodb://localhost:27017/"))
db = client["restaurantDB"]
collection = db["locations"]

googleMapsAPIKey = os.getenv("GOOGLE_MAPS_API_KEY")

@mcp.tool
def store_restaurants(location_data:dict) ->str:
    """
    Stores location and the resturants that are 1 miles away

    """

    location = location_data.get("location")
    userLocation = location_data.get("user_location",{})
    restaurants = location_data.get("restaurants",[])

    if not location or not restaurants:
        return "bad input"
    
    collection.update_one(
        {"location", location},
        {"$set":{"restaurants":restaurants}},
        upsert=True
    )
    return f"Stored resturaunts around: {location}"

if __name__ == "__main__":
    mcp.run()