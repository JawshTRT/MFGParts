from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_top_3_ebay(item_query):
    driver = webdriver.Chrome()  # Selecting which search tool to use Google Chrome or Firefox, Edge, etc.
    # Prompting the user what they want to look for
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={item_query.replace(' ', '+')}"  # <--- Ebay's URL, replacing spaces with '+'s
    driver.get(ebay_url)

    # Giving some time for the search tool to load
    wait = WebDriverWait(driver, 10)  # Function Parameters (Driver, time in seconds)
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "li.s-item")))

    # Storing the first 3 results
    search_results = driver.find_elements(By.CSS_SELECTOR, "li.s-item")[
                     2:5]  # <--- List indexing for the first 3 items skipping the first 2 because they appear to be ghost links?

    # For each search result we need to extract the name, brand, and price

    listings = []
    for search in search_results:

        name = search.find_element(By.CSS_SELECTOR, ".s-item__title").text
        # On ebay, the "brand" is often in the "data-brand" attribute or inside a span:

        #Brand often in the subtitle block but may not always exist
        try:
            brand = search.find_element(By.CSS_SELECTOR, ".s-item__subtitle .s-item__subtitle--tagblock").text
        except:
            brand = "Unknown"

    # Price sometimes split into whole + fraction// only on amazon not on ebay

        try:
            price = search.find_element(By.CSS_SELECTOR, ".s-item__price").text

        except:
            price = "N/A"

        link = search.find_element(By.CSS_SELECTOR, ".s-item__link").get_attribute("href")

        listings.append({"name": name, "brand": brand,
                     "price": price, "link": link})  # Each listing entry will use a dictionary to store the price, brand, and name

    driver.quit()
    return listings
    # For troubleshooting incorporating a link to the webpage


if __name__ == "__main__":
    item = input("Enter an item to search on ebay: ")
    top3 = get_top_3_ebay(item)
    for i, listing in enumerate(top3, 1):
        print(f"{i})  Title: [{listing['name']}] Brand:[{listing['brand']}] Price: [{listing['price']}] URL: [{listing["link"]}]\n")

