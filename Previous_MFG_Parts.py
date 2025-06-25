from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import locale # <---- currency formatting and conversion
from urllib.parse import urlparse # <---- cleaning up URLs

def USD_Convert(price):
    #Checking the first character of the string price that denotes currency to see if it is equal to a dollar sign
    if price[1:0] != '$':
        pass

def URL_Fetcher(browser):
    """
    :URL_Fetcher:
        Checks a URL to determine if it is a valid item page URL
    :param Link:
        The Link to the webpage
    :param browser:
        The driver object to access the webpage
    :return:
        A list of 7 links to sift through items and their specifications
    """
    Link = browser.find_element(By.CSS_SELECTOR, "ul.srp-results").find_elements(By.CSS_SELECTOR, "li.s-item") # <--- List indexing for the first 3 items skipping the first 2 because they appear to be ghost links?
    CleanLinks = []
    seen_urls = set()
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
        if len(CleanLinks) == 12:
            break
    return CleanLinks

def get_top_3_ebay(item_query):
    driver = webdriver.Chrome()  # Selecting which search tool to use Google Chrome or Firefox, Edge, etc.
    # Prompting the user what they want to look for
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={item_query.replace(' ', '+')}"  # <--- Ebay's URL, replacing spaces with '+'s
    driver.get(ebay_url)



    # Giving some time for the search tool to load
    wait = WebDriverWait(driver, 10)  # Function Parameters (Driver, time in seconds)
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "ul.srp-results"))) # <-- only shows up once ebay has rendered actual search hits


    # Storing the first 3 results via list slicing
    search_results = URL_Fetcher(driver)  # <--- List indexing for the first 3 items skipping the first 2 because they appear to be ghost links?



    listings = []
    for search in search_results:


        # For each search result we need to extract the name, brand, and price
        name = search.find_element(By.CSS_SELECTOR, ".s-item__title").text
        # On ebay, the "brand" is often in the "data-brand" attribute or inside a span:

        #Brand often in the subtitle block but may not always exist
        cond = search.find_element(By.CSS_SELECTOR, ".s-item__subtitle").text

        # Price sometimes split into whole + fraction// only on amazon not on ebay


        price = search.find_element(By.CSS_SELECTOR, ".s-item__price").text

        link = search.find_element(By.CSS_SELECTOR, ".s-item__link").get_attribute("href")

        listings.append({"name": name, "cond": cond,
                     "price": price, "link": link})  # Each listing entry will use a dictionary to store the price, brand, and name

    driver.quit()
    return listings
    # For troubleshooting incorporating a link to the webpage


if __name__ == "__main__":
    item = input("Enter an item to search on ebay: ")
    top3 = get_top_3_ebay(item)
    for i, listing in enumerate(top3, 1):
        print(f"{i})  Title: [{listing['name']}]\n Condition: [{listing['cond']}]\n Price: [{listing['price']}]\n URL: [{listing["link"]}]\n\n")

