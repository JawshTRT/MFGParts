from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import locale  # <---- Currency formatting and conversion
import time

def Driver_Init():
    """
    Initializes the selenium webdriver via chromedriver
    :return driver:
        The webdriver instance to be returned
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") #<---- Considering running headless
    # Selecting which search tool to use Google Chrome or Firefox, Edge, etc.
    driver = webdriver.Chrome(options=options)
    stealth(driver, vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer=
    "Intel Iris OpenGL Engine",
            fix_hairline=True)
    return driver
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
    """Reads the respective csv file
    :param filename:
        The name of the csv file in the workspace directory to be read
    :return search_terms:
    The list of search terms for the webscraper to search on ebay
    :return SKU:
    The list of SKUs for the webscraper
    """
    df = pd.read_csv(filename)
    # Extracting the file column full of item names
    search_terms = df['Name'].dropna().astype(str).tolist()
    SKU = df['SKU'].dropna().dropna().astype(str).tolist()
    return search_terms, SKU
def URL_Fetcher(browser, item_query):
    """
    Checks a url to determine if it is a valid item page on the URL...
    :param item_query:
        Item to be searched through ebay
    :param browser:
        The driver object to access the webpage
    :return CleanLinks:
        A list of 7 links to sift through items and their specifications
    """
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={item_query.replace(' ', '+')}"  # <--- Ebay's URL, replacing spaces with '+'s
    browser.get(ebay_url)
    wait = WebDriverWait(browser, 20)  # Waiting even longer (10 more seconds for the search results list to exit)
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "ul.srp-results")))  # <-- only shows up once ebay has rendered actual search hits
    WebDriverWait(browser, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")

    # Results are sometimes lazy loaded so scroll at least once
    browser.execute_script("window.scrollBy(0, 1000);")
    time.sleep(1)

    Link = browser.find_element(By.CSS_SELECTOR, "ul.srp-results").find_elements(By.CSS_SELECTOR, "li.s-item")


    CleanLinks = []
    seen_urls = set()
    print(f"{len(Link)} listings found")  # <---- Debug


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

    driver = Driver_Init()
    # Storing the results in the function URL_Fetcher function
    search_results = URL_Fetcher(driver, item_query)
    if len(search_results) == 0:
        for attempt in range(1, 3 + 1):
            print(f"Attempt {attempt}/{3}...")
            driver = Driver_Init()
            try:
                search_results = URL_Fetcher(driver, item_query)
                if len(search_results) > 0:
                    break
            except Exception as e:
                print(f"No results, retrying in {2}s...")
            time.sleep(2)


    listings = []
    for search in search_results:
        # Fetching name
        name = search.find_element(By.CSS_SELECTOR, ".s-item__title").text
        # Condition sometimes the condition has a different CSS selector will look into later
        #TODO: Enter a new exception clause to tackle varying condition tags on item listings
        try:
            cond = search.find_element(By.CSS_SELECTOR, ".s-item__subtitle").text
        except NoSuchElementException:
            cond = "Invalid Condition element"
        # Price
        price = search.find_element(By.CSS_SELECTOR, ".s-item__price").text
        # Link
        link = search.find_element(By.CSS_SELECTOR, ".s-item__link").get_attribute("href")

        # Each listing entry will use a dictionary to store the price, brand, and name
        listings.append({"name": name, "cond": cond,
                         "price": price, "link": link})

    #Close the driver
    driver.quit()
    return listings

if __name__ == "__main__":
    products, SKU = ImportCSv('Sample Parts List - Sheet1.csv')
    results = []
    for item, number in zip(products, SKU):
        top_items = get_top_3_ebay(item)
        summation, count = 0.0, 0.0
        for rank, top_item in enumerate(top_items, start =1):
            top_item['sku'] = number
            summation += float(top_item['price'][1:].replace(',', '')) # <---- Excluding ($) from summation to avoid type mismatch
            count += 1.0
            results.append(top_item)
            print(f"{rank}. Name: [{top_item['name']}]\n Condition: [{top_item['cond']}]\nPrice: [{top_item['price']}]\n Link: [{top_item['link']}\nSKU: [{top_item['sku']}]\n")
        print(f"Average: ${summation/count:.2f}")
    # Converting to dataframe
    df = pd.DataFrame(results)
    df.to_csv("ebay_results.csv", index=False)

    print("Saved", len(df), "rows to ebay_results.csv")

