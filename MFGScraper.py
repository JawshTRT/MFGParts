from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import locale  # <---- currency formatting and conversion

import time


def USD_Convert(price):
    """
    Converts any non USD price to USD
    :param price:
        The price to be converted
    :return:
    """
    if price[1:0] != '$':
        pass
def ImportCSv(filename):
    """Reads the respective csv file"""
    df = pd.read_csv(filename)
    # Extracting the file column full of item names
    search_terms = df['Name'].dropna().astype(str).tolist()
    return search_terms
def URL_Fetcher(browser):
    """
    Checks a url to determine if it is a valid item page on the URL...
    :param browser:
        The driver object to access the webpage
    :return CleanLinks:
        A list of 7 links to sift through items and their specifications
    """

    Link = browser.find_element(By.CSS_SELECTOR, "ul.srp-results").find_elements(By.CSS_SELECTOR, "li.s-item")
    #    if len(Link) > 0: #<------ will stall if there are no results
    #        break
    CleanLinks = []
    seen_urls = set()
    print(len(Link))  # <---- Debug
    # Iterating through links to see if there are any invalid links
    for l in Link:

        try:
            href = l.find_element(By.CSS_SELECTOR, "a.s-item__link").get_attribute("href")
            title = l.find_element(By.CSS_SELECTOR, ".s-item__title").text
            price = l.find_element(By.CSS_SELECTOR, ".s-item__price").text
        except NoSuchElementException:
            continue
        if "/itm/" not in href:
            continue

        if href in seen_urls:
            continue
        seen_urls.add(href)
        CleanLinks.append(l)

        # Limiting it to the first 12 links
        if len(CleanLinks) == 6:
            break
    return CleanLinks
def get_top_3_ebay(item_query):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(
        options=options)  # Selecting which search tool to use Google Chrome or Firefox, Edge, etc.

    stealth(driver, vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer=
    "Intel Iris OpenGL Engine",
            fix_hairline=True)

    # Prompting the user what they want to look for
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={item_query.replace(' ', '+')}"  # <--- Ebay's URL, replacing spaces with '+'s
    driver.get(ebay_url)

    wait = WebDriverWait(driver, 20)  # Waiting even longer (10 more seconds for the search results list to exit)
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "ul.srp-results")))  # <-- only shows up once ebay has rendered actual search hits
    WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")

    # Even more debugging
    print("URL\n", driver.current_url)
    print("Title\n", driver.title)
    html = driver.page_source
    print("HTML", html[:500].replace("\n", " "))


    listings = []
    for search in search_results:
        # Fetching name
        name = search.find_element(By.CSS_SELECTOR, ".s-item__title").text
        # Title
        cond = search.find_element(By.CSS_SELECTOR, ".s-item__subtitle").text
        # Price
        price = search.find_element(By.CSS_SELECTOR, ".s-item__price").text
        # Link
        link = search.find_element(By.CSS_SELECTOR, ".s-item__link").get_attribute("href")

        # Each listing entry will use a dictionary to store the price, brand, and name
        listings.append({"name": name, "cond": cond,
                         "price": price, "link": link})

    driver.quit()
    return listings
    # For troubleshooting incorporating a link to the webpage


if __name__ == "__main__":
    products = ImportCSv('Sample Parts List - Sheet1.csv')
    results = []
    for item in products:
        top_items = get_top_3_ebay(item)
        for rank, top_item in enumerate(top_items, start =1):
            results.append(top_item)
            print(f"{rank}. Name: [{top_item['name']}]\n Cond: [{top_item['brand']}]Price: [{top_item['price']}]\n Link: [{top_item['link']}]")