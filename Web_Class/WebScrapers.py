from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Web_Class.BaseScraper import BaseScraper
from selenium.webdriver.common.by import By


class EbayScraper(BaseScraper):
    """
    Inherits from the BaseScraper abstract base class
    :var BaseScraper:
        Abstract base class that inherits from BaseScraper
    """

    def get_search_url(self, query: str):
        return f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}"

    def select_result_items(self):
        return self.driver.find_element(By.CSS_SELECTOR, "ul.srp-results").find_elements(By.CSS_SELECTOR, "li.s-item")

    def parse_item(self, element):
        title = element.find_element(By.CSS_SELECTOR, ".s-item__title").text
        price = element.find_element(By.CSS_SELECTOR, ".s-item__price").text
        url = element.find_element(By.CSS_SELECTOR, ".s-item__link").get_attribute("href")
        try:
            condition = element.find_element(By.CSS_SELECTOR, ".s-item__subtitle").text
        except NoSuchElementException:
            condition = "Invalid Condition Element"
            print("Invalid Condition Element found")
        return {"title": title, "price": price, "url": url, "condition": condition}
    def WaitResults(self):
        """Waits for the web page to finish loading the results based on the selector tag"""
        wait = WebDriverWait(self.driver, 20)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        #WebDriverWait(self.driver, 20).until(lambda d: d.execute_script("return document.querySelector('ul.srp-results')") == "complete")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.s-item")))
    def check_Results(self):
        no_match = self.driver.find_elements(By.XPATH,"//*[contains(text(), 'No exact matches found')]")
        if no_match:
            print("No exact matches found")
            return False
        else:
            return True
class RadwellScraper(BaseScraper):
    """
    Inherits from the BaseScraper abstract base class
    :var BaseScraper:
        Abstract base class that inherits from BaseScraper
    """

    def get_search_url(self, query):
        return (f"https://www.radwell.com/Search/Advanced?qPartNumber={query.replace('', '+')}")

    def select_result_items(self):
        # Radwell uses a table of <tr> rows for results
        return self.driver.find_elements(By.CSS_SELECTOR, "table#SearchResultsGrid tbody tr")

    def parse_item(self, element):
        """
        Separates the search results into individual items
        :param element:
             The search results
        :var name:
            The name of the item
        :var brand:
            The brand of the item
        :var price:
            The price of the item
        :var url:
            The url link of the item
        :return:
        A dictionary with the item's details
        """
        name = element.find_element(By.CSS_SELECTOR, "td:nth-child(1) a").text
        brand = element.find_element(By.CSS_SELECTOR, "td:nth-child(2) a").text
        price = element.find_element(By.CSS_SELECTOR, "td:nth-child(6) a").text
        url = element.find_element(By.CSS_SELECTOR, "td:nth-child(1) a").get_attribute("href")

        return {"name": name, "brand": brand, "price": price, "url": url}
    def Check_Results(self):
        return True
