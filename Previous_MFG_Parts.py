from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import locale  # <---- currency formatting and conversion
import time


def USD_Convert(price):
    # Checking the first character of the string price that denotes currency to see if it is equal to a dollar sign
    if price[1:0] != '$':
        pass


def URL_Fetcher(browser):
    """
    Checks a url to determine if it is a valid item page on the URL...
    :param browser:
        The driver object to access the webpage
    :return CleanLinks:
        A list of 7 links to sift through items and their specifications
    """


    # First find all the entries
    #while True:
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
            title = l.find_element(By.CSS_SELECTOR, "h3.s-item__title").text
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
        if len(CleanLinks) == 12:
            break
    return CleanLinks


def get_top_3_ebay(item_query):
    driver = webdriver.Chrome()  # Selecting which search tool to use Google Chrome or Firefox, Edge, etc.
    # Prompting the user what they want to look for
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={item_query.replace(' ', '+')}"  # <--- Ebay's URL, replacing spaces with '+'s
    driver.get(ebay_url)

    # Giving some time for the search tool to load
    wait = WebDriverWait(driver, 20)  # Waiting even longer (10 more seconds for the search results list to exit)
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "ul.srp-results")))  # <-- only shows up once ebay has rendered actual search hits


    # Accepting cookie banner if it is present
    try:
        cookie = wait.until(EC.element_to_be_clickable((By.ID, "gdpr-banner-accept")))
        cookie.click()
    except:
        pass
    # Results are sometimes lazy loaded so scroll at least once
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(1)

    # Storing the results in the function URL_Fetcher
    search_results = URL_Fetcher(driver)

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
    item = input("Enter an item to search on ebay: ")
    top3 = get_top_3_ebay(item)
    for i, listing in enumerate(top3, 1):
        print(
            f"{i})  Title: [{listing['name']}]\n Condition: [{listing['cond']}]\n Price: [{listing['price']}]\n URL: [{listing["link"]}]\n\n")
