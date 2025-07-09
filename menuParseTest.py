import re
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

def price_parse(_text: str) -> float:
    match = re.search(r'\$?(\d+\.\d{2})', _text)
    return float(match.group(1)) if match else None

def find_square_menu_url(homepage_url: str) -> str:
    """
    Given a homepage URL, find a Square-hosted menu link.
    """
    try:
        html = requests.get(homepage_url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "square.site" in href:
                full_url = urljoin(homepage_url, href)
                print(f"[INFO] Found Square menu URL: {full_url}")
                return full_url
    except Exception as e:
        print(f"[ERROR] Could not find Square menu link: {e}")
    return None

def scrape_square_menu(homepage_url: str, budget: int, location_name: str = "Medford") -> list:
    """
    Full flow:
    1. Start at homepage
    2. Find square.site link
    3. Navigate to square site with Playwright
    4. Click on location (e.g. Medford)
    5. Scrape menu items and prices
    """
    menu_url = find_square_menu_url(homepage_url)
    if not menu_url:
        return []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            print(f"[INFO] Opening Square site: {menu_url}")
            page.goto(menu_url, timeout=20000)

            print(f"[INFO] Clicking location: {location_name}")
            page.wait_for_selector(f"text={location_name}", timeout=8000)
            page.click(f"text={location_name}")
            page.wait_for_load_state("networkidle")

            content = page.content()
            browser.close()

        soup = BeautifulSoup(content, "html.parser")
        texts = list(soup.stripped_strings)

        items = []
        for i, text in enumerate(texts):
            price = price_parse(text)
            if price:
                name = texts[i - 1] if i > 0 else "Unknown Item"
                if 0 < price <= budget:
                    items.append((name.strip(), price))

        print(f"[INFO] Found {len(items)} menu items under ${budget}")
        return items

    except Exception as e:
        print(f"[ERROR] Failed to scrape Square menu: {e}")
        return []
# === Test ===
urlsList = ["http://www.tenochmexican.com/", "http://surabbqkorean.com/"]
budget = 17

result = scrape_square_menu("http://www.tenochmexican.com/", budget=17, location_name="Medford")
print("***************************")
print(result)