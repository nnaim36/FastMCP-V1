from fastapi import FastAPI
from fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import itertools
import re

mcp = FastMCP()

@mcp.tool
def find_local_resturants


@mcp.tool
def scrape_menu() -> dict:
    """
    scapes the menus of resturants for food items and their prices.
    the output is the combinations options that are in the users budget.
    """

if __name__ == "__main__":
    mcp.run()