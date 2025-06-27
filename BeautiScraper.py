import sys, requests
from urllib.parse import urlparse, urlunparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pandas as pd
from urllib3 import Retry


def Listings(soup):
    Lists = []
    results = soup.select(".srp-main--isLarge .srp-grid .s-item")
    for item in results:
        title = item.select_one(".s-item__title").getText(strip=True)
        price = item.select_one(".s-item__price").getText(strip=True)
        link = item.select_one(".s-item__link")['href']
        Lists.append([title, price, link])
    return Lists


def get_top_3_ebay(item_query):
    """
    Searches ebay for the given item

    :param item_query:
        The item to be searched for on ebay
    :return listings:
    The list of listings from the search results
    """
    # Fetching the search-results page by parsing it with
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={item_query.replace(' ', '+')}"  # <--- Ebay's URL, replacing spaces with '+'s

    # Setting arguments for .get() function call
    params = {"_nkw": item_query} # <-- Ebay's URL query parameter key, tells their server what you're looking for
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/114.0.0.0 Safari/537.36"}


    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
                            "Accept": "text/html,application/xhtml+xml, application/xml; q=0.9, */*;q=0.8",
                            "Accept-Language": "en-US,en;q=0.9",
                            "Connection": "keep-alive",})
    session.get("https://www.ebay.com/", timeout=10)
    retries = Retry(total= 3, backoff_factor = 0.5,
                    status_forcelist = [429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        resp = session.get(ebay_url, params=params, headers=headers, timeout=10)
        resp.raise_for_status() # <-- checks the HTTP status code and raises a requests.HTTPError if its a client or server error
    except requests.exceptions.ReadTimeout:
        print("Request timed out-retrying once more...")
        resp = requests.get(ebay_url, params=params, headers=headers, timeout=30)
    soup = BeautifulSoup(resp.text, "html.parser")
    results = soup.select("ul.srp-results li.s-item")[:3] # 3 search results

    print("Fetched URL:", resp.url)
    print("Status code:", resp.status_code)

    snippet = resp.text[:1000].replace("\n", "")
    print("HTML head snippet:", snippet)

    listings = []
    for item in results:

        #Gathering the necessary properties of the item
        link = item.select_one("a.s-item__link")['href']
        title = item.select_one(".s-item__title")
        price = item.select_one(".s-item__price")
        if not (link and title and price):
            continue

        #Cleaning up the url
        p = urlparse(link)
        clean = urlunparse((p.scheme, p.netloc, p.path, "", "", "")) #<-- These are the main parts of the url we want to keeep
        # Scheme = "https" or "http"
        # netloc = network location Ex. www.ebay.com
        # path = the resources location on the server -> "/itm/12345


        # Appending result properties to a list

        listings.append({"name": title.get_text(strip=True), "price": price.get_text(strip=True),
                         "link": clean})

    return listings

if __name__ == "__main__":
    item = input("Enter an item to search on ebay")
    top3 = get_top_3_ebay(item)

    for i, item in enumerate(top3, 1):
        print(f"{i}. Name: [{item['name']}]\n Price: [{item['price']}]\n URL: [{item['link']}]")
