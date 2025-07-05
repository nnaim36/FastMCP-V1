from fastapi import FastAPI
from fastmcp import FastMCP
from datetime import datetime
from zoneinfo import ZoneInfo
import time
import uvicorn
import requests
import os

mcp = FastMCP(
    name="Local-Time",
    host="127.0.0.1",
    port=8001
)

@mcp.tool
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


if __name__ == "__main__":
    mcp.run()