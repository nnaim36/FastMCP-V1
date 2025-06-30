from fastapi import FastAPI
from fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import itertools
import re

mcp = FastMCP()

def price_parse(_text:str)->float:
    match = re.search(r'\$?(\d+\.\d{2})', _text)
    return float(match.group(1)) if match else None

@mcp.tool
def find_local_resturants(_location:str) -> list:
    """
    Find resturants near user's location using duckduckgo
    """
    query = f"resturants near {_location}"
    url = f"http:/duckduck.com/html/?={query.replace(' ','+')}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    links=[]
    for link in soup.find_all('a',href=True):
        href = a['href']
        if "http" in href and not any(bad in href for bad in ["duckduckgo","bing", "yahoo"]):
            links.append(href)

    return list(set(links))[:20] #set to return only 20 links

@mcp.tool
def scrape_menu(_urlsList:list, _budget:int) -> dict:
    """
    scapes the menus of resturants for food items and their prices.
    the output is the combinations options that are in the users budget.
    """

    menuItems = []

    for url in urls:
        try:
            html = requests.get(url, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")
            texts = soup.stripped_strings
            for text in texts:
                price = parse_price(text)
                if price:
                    name = text.replace(f"${price}", "").strip()
                    if 0 < price <= budget:
                        menuItems.append((name, price))
        except:
            continue

    # Generate combos
    combos = []
    for i in range(1, len(menuItems) + 1):
        for combo in itertools.combinations(menuItems, i):
            total = sum(item[1] for item in combo)
            if total <= budget:
                combos.append((combo, round(total, 2)))

    combos.sort(key=lambda x: -x[1])
    return {
        "menu_items": menuItems,
        "best_combinations": combos[:10]
    }

if __name__ == "__main__":
    mcp.run()