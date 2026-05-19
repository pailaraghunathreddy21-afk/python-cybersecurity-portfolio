import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from colorama import Fore, init
import random
import time
import json
import csv

# Initialize colorama
init(autoreset=True)

# ==========================================
# CONFIGURATION
# ==========================================

URL = "https://books.toscrape.com/"

ua = UserAgent()

# Proxy Pool
PROXIES = [
    None
]

# Browser Headers
HEADERS_LIST = [
    {
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    },
    {
        "Accept-Language": "en-GB,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
    }
]

# ==========================================
# SAVE JSON
# ==========================================

def save_to_json(data):

    with open("books.json", "w") as file:

        json.dump(data, file, indent=4)

    print(Fore.GREEN + "\n[+] Data saved to books.json")

# ==========================================
# SAVE CSV
# ==========================================

def save_to_csv(data):

    with open("books.csv", "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(["Title", "Price"])

        for item in data:

            writer.writerow([item["title"], item["price"]])

    print(Fore.GREEN + "[+] Data saved to books.csv")

# ==========================================
# SCRAPER ENGINE
# ==========================================

def scrape_website():

    retries = 3

    scraped_data = []

    for attempt in range(retries):

        headers = random.choice(HEADERS_LIST)

        headers["User-Agent"] = ua.random

        proxy = random.choice(PROXIES)

        print(Fore.CYAN + f"\n[+] Attempt {attempt + 1}")

        print(Fore.YELLOW + "[+] Using User-Agent:")
        print(headers["User-Agent"])

        try:

            response = requests.get(
                URL,
                headers=headers,
                proxies={
                    "http": proxy,
                    "https": proxy
                } if proxy else None,
                timeout=10
            )

            print(Fore.GREEN + f"\n[+] Status Code: {response.status_code}")

            # Handle Anti-Bot Detection
            if response.status_code in [403, 429, 503]:

                print(Fore.RED + "[-] Anti-bot protection detected")

                wait = 2 ** attempt

                print(Fore.YELLOW + f"[+] Waiting {wait} seconds...")

                time.sleep(wait)

                continue

            soup = BeautifulSoup(response.text, "html.parser")

            books = soup.find_all("article", class_="product_pod")

            print(Fore.MAGENTA + f"\n[+] Found {len(books)} books\n")

            for index, book in enumerate(books[:10], start=1):

                title = book.find("h3").find("a")["title"]

                price = book.find(
                    "p",
                    class_="price_color"
                ).text.replace("Â", "")

                book_data = {
                    "title": title,
                    "price": price
                }

                scraped_data.append(book_data)

                print(Fore.WHITE + f"{index}. {title}")

                print(Fore.GREEN + f"   Price: {price}\n")

            # Save files
            save_to_json(scraped_data)

            save_to_csv(scraped_data)

            return

        except requests.exceptions.RequestException as e:

            print(Fore.RED + f"\n[-] Request Failed: {e}")

            wait = 2 ** attempt

            print(Fore.YELLOW + f"[+] Retrying in {wait} seconds...")

            time.sleep(wait)

# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    print(Fore.BLUE + "\n=== PROFESSIONAL WEB SCRAPER ===")

    delay = random.uniform(1, 4)

    print(Fore.CYAN + f"\n[+] Sleeping for {delay:.2f} seconds")

    time.sleep(delay)

    scrape_website()