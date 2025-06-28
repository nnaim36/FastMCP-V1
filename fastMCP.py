from fastapi import FastAPI
from fastmcp import FastMCP
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import os

mcp = FastMCP()

@mcp.tool
def add(a: int, b: int) -> int:
    """Adds two integer numbers together."""
    return a + b

@mcp.resource("resource://config")
def get_config() -> dict:
    """Provides the application's configuration."""
    return {"version": "1.0", "author": "MyTeam"}

@mcp.resource("greetings://{name}")
def personalized_greeting(name: str) -> str:
    """Generates a personalized greeting for the given name."""
    return f"Hello, {name}! Welcome to the MCP server."

@mcp.get("/get-local-time")
def get_local_time(timezone: str = "UTC") -> str:
    """
    Return the current time for the time zone tha the user is in
    the backup return will be universal time(UTC).
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
        return now.isoformat()
    except Exception:
        now = datetime.now(datetime.timezone.utc)
        return now.isoformat() + "z"


@mcp.get("get-location")
def getlocation()->str:
    """
    receive the users location.
    """
    return "we have not figure this one out yet."