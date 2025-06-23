from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()  # or Firefox, Edge, etc.
driver.get("https://example.com/")

print()
element = driver.find_element(By.TAG_NAME, "h1")
print(element.text)

driver.quit()