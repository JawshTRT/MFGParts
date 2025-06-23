from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random
driver = webdriver.Chrome()  # Selecting which search tool to use Google Chrome or Firefox, Edge, etc.


# Prompting the user what they want to look for
item = input("What are you looking for?")

ebay_url = f"https://www.radwell.com/Search/Advanced?PartNumber={item.replace(' ', '+')}" # <--- Radwell's URL, replacing spaces with '+'s
driver.get(ebay_url)




# Giving some time for the search tool to load
wait = WebDriverWait(driver, 10) # Function Parameters (Driver, time in seconds)
wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr")))

#Storing the results
search_results = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")[:3] # <--- List indexing for the first 3 items


# For each search result we need to extract the name, brand, and price
listings = []


for search in search_results:
    time.sleep(random.uniform(2, 5))

    name = search.find_element(By.CSS_SELECTOR, "td:nth-child(1) a").text
    brand = search.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    price = search.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
    link = search.find_element(By.CSS_SELECTOR, "td:nth-child(1) a").get_attribute("href")

    listings.append({"name": name, "brand": brand, "price": price, "link": link})

for idx, item in enumerate(listings, 1):
    print(f"{idx})\n {item['brand']}\n {item['price']}\n Link: {item['link']}")

driver.quit()