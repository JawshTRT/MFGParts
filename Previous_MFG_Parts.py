from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, random
driver = webdriver.Chrome()  # Selecting which search tool to use Google Chrome or Firefox, Edge, etc.






# Prompting the user what they want to look for
item = input("What are you looking for?")

ebay_url = f"https://www.radwell.com/Search/Advanced?PartNumber={item.replace(' ', '+')}" # <--- Radwell's URL, replacing spaces with '+'s
driver.get(ebay_url)




# Giving some time for the search tool to load
wait = WebDriverWait(driver, 20) # Function Parameters (Driver, time in seconds)
q = wait.until(EC.presence_of_element_located((By.NAME, "q")))
q.send_keys(f"site:radwell.com {item}")
q.send_keys(Keys.RETURN)


#wait for results links to load
wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#search a")))


#Only collecting links from radwell.com hrefs
all_links = driver.find_elements(By.CSS_SELECTOR, "div#search a")


radwell_links = []
for link in all_links:
    href = link.get_attribute("href")
    if href and "radwell.com" in href:
        radwell_links.append(href)

    # Breaking out of the loop as soon as the size of the list is greater than 3
    if len(radwell_links) >= 3:
        break



listings = []
    #-- 2. Visit each top-3 Radwell result and scape------
for link in radwell_links:
    driver.get(link)
    # Try accepting the cookies if present
    try:
        driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
    except NoSuchElementException:
        pass

    # wait for the table rows
    wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody//tr")))
    row = driver.find_element(By.XPATH, "(//table//tbody//tr)[1]")
    name = link.find_element(By.CSS_SELECTOR, "td:nth-child(1) a").text
    brand = link.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    price = link.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
    listings.append({"name": name, "brand": brand, "price": price})



driver.quit()

for idx, item in enumerate(listings, 1):
    print(f"{idx})\n {item['brand']}\n {item['price']}\n Link: {item['link']}")

driver.quit()