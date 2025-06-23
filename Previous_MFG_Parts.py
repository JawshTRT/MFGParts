from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, random
driver = webdriver.Chrome()  # Selecting which search tool to use Google Chrome or Firefox, Edge, etc.


# Prompting the user what they want to look for
item = input("What are you looking for?")
ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={item.replace(' ', '+')}" # <--- Ebay's URL, replacing spaces with '+'s
driver.get(ebay_url)

# Giving some time for the search tool to load
wait = WebDriverWait(driver, 10) # Function Parameters (Driver, time in seconds)
wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.s-item")))

#Storing the results
search_results = driver.find_elements(By.CSS_SELECTOR, "li.s-item")[:3] # <--- List indexing for the first 3 items


# For each search result we need to extract the name, brand, and price
listings = []
for search in search_results:
    title_elems = search.find_elements(By.CSS_SELECTOR, ".s-item__title")
    title = title_elems[0].text if title_elems else "Unknown"
    # On ebay, the "brand" is often in the "data-brand" attribute or inside a span:

    brand_elems = search.find_elements(By.CSS_SELECTOR, ".s-item__subtitle--tagblock")

    brand = brand_elems[0].text if brand_elems else "Unknown"

    # price sometimes split into whole + fraction// only on amazon not on ebay
    price = search.find_element(By.CSS_SELECTOR, ".s-item__price").text

    listings.append({"name": title, "brand": brand, "price": price}) # Each listing entry will use a dictionary to store the price, brand, and name

    #For troubleshooting incorporating

for idx, item in enumerate(listings, 1):
    print(f"{idx})\n {item['brand']}\n {item['price']}\n")


driver.quit()