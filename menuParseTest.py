import re
import requests
import itertools
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from pathlib import Path

# === Utility Functions ===
def price_parse(_text: str) -> float:
    match = re.search(r'\$?(\d+\.\d{2})', _text)
    return float(match.group(1)) if match else None

# === Menu Discovery ===
def discover_menu_pages(base_url: str, max_depth=2) -> list:
    visited = set()
    to_visit = [base_url]
    found_menu_links = []

    while to_visit and max_depth > 0:
        next_round = []
        for url in to_visit:
            if url in visited:
                continue
            visited.add(url)
            try:
                html = requests.get(url, timeout=10).text
                soup = BeautifulSoup(html, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = urljoin(url, a['href'])
                    text = a.get_text(strip=True).lower()
                    if any(kw in href.lower() or kw in text for kw in ["menu", "order", "eat", "food", "location"]):
                        found_menu_links.append(href)
                        next_round.append(href)
            except:
                continue
        to_visit = next_round
        max_depth -= 1

    return list(set(found_menu_links))

# === Scrapers ===
def scrape_html_menu(url: str, budget: int) -> list:
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        texts = list(soup.stripped_strings)
        items = []
        for i, text in enumerate(texts):
            price = price_parse(text)
            if price:
                name = texts[i - 1] if i > 0 else "Unknown Item"
                if 0 < price <= budget:
                    items.append((name.strip(), price))
        return items
    except Exception as e:
        print(f"[ERROR] HTML scrape failed: {e}")
        return []

def scrape_square_menu(url: str, budget: int, location_name: str = "Medford") -> list:
    try:
        items = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000)
            page.wait_for_selector(f"text={location_name}", timeout=8000)
            page.click(f"text={location_name}")
            page.wait_for_load_state("networkidle")
            content = page.content()
            browser.close()
        soup = BeautifulSoup(content, "html.parser")
        texts = list(soup.stripped_strings)
        for i, text in enumerate(texts):
            price = price_parse(text)
            if price:
                name = texts[i - 1] if i > 0 else "Unknown Item"
                if 0 < price <= budget:
                    items.append((name.strip(), price))
        return items
    except Exception as e:
        print(f"[ERROR] Square scrape failed: {e}")
        return []

# === Orchestrator ===
def scrape_menu(homepages: list, budget: int) -> dict:
    all_items = []
    for homepage in homepages:
        print(f"[INFO] Searching: {homepage}")
        candidate_links = discover_menu_pages(homepage, max_depth=2)

        best_items = []
        for link in candidate_links:
            print(f"[TRY] {link}")
            if link.endswith(".pdf"):
                continue  # placeholder: add scrape_pdf_menu here
            elif any(p in link for p in ["square.site", "toasttab", "grubhub"]):
                best_items = scrape_square_menu(link, budget)
            else:
                best_items = scrape_html_menu(link, budget)
            if best_items:
                break

        print(f"[FOUND] {len(best_items)} items from {homepage}")
        all_items.extend(best_items)

    combos = []
    for i in range(1, len(all_items) + 1):
        for combo in itertools.combinations(all_items, i):
            total = sum(item[1] for item in combo)
            if total <= budget:
                combos.append((combo, round(total, 2)))
    combos.sort(key=lambda x: -x[1])

    return {
        "menu_items": all_items,
        "best_combinations": combos[:10]
    }
# === Test ===
urlsList = ["http://www.tenochmexican.com/", "http://surabbqkorean.com/"]
budget = 17

result = scrape_menu(urlsList, budget)
print("***************************")
print(result)