from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()  # Selecting which search tool to use Google Chrome or Firefox, Edge, etc.


# Prompting the user what they want to look for
item = input("What are you looking for?")
ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={item.replace(' ', '+')}" # <--- Ebay's URL, replacing spaces with '+'s
driver.get(ebay_url)

# Giving some time for the search tool to load
wait = WebDriverWait(driver, 10) # Function Parameters (Driver, time in seconds)
wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")))

#Storing the results
search_results = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")


# For each search result we need to extract the name, brand, and price
listings = []
for search in search_results:
    title = search.find_elements(By.CSS_SELECTOR, "h2 a span").text
    # On Amazon, the "brand" is often in the "data-brand" attribute or inside a span:
    try:
        brand = search.get_attribute("data brand") or \
                search.find_element(By.CSS_SELECTOR, ".a-row .a-size-base").text
    except:
        brand = "_"

    # price sometimes split into whole + fraction:
    try:
        whole = search.find_element(By.CSS_SELECTOR, ".a-row .a-size-base").text
        frac = search.find_element(By.CSS_SELECTOR, ".a-price-fraction").text
        price = f"${whole}{frac}"
    except:
        price = "_"

    listings.append({"name": title, "brand": brand, "price": price}) # Each listing entry will use a dictionary to store the price, brand, and name




driver.quit()