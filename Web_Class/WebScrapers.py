from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Web_Class.BaseScraper import BaseScraper
from selenium.webdriver.common.by import By
import urllib


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
        return f"https://www.radwell.com/Search/Advanced?qPartNumber={query.replace(' ', '+')}"
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
    def check_Results(self):
        no_match = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'We couldn't find your item. Try refining your search.')]")
        if no_match:
            print("No exact matches found")
            return False
        else:
            return True
    def WaitResults(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".k-loading-mask")))
        rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#ResultGrid .k-grid-content tr")))
class GraingerScraper(BaseScraper):
    """
        Inherits from the BaseScraper abstract base class
        :var BaseScraper:
            Abstract base class that inherits from BaseScraper
        """
    def get_search_url(self, query):
        return f"https://www.grainger.com/search?searchQuery={query.replace(' ', '%20')}"
    def select_result_items(self):
        return self.driver.find_element(By.CSS_SELECTOR, "ul#searchResultsList > li.search-results-item")
    def parse_item(self, element) -> dict:
        link_el = element.find_element(By.CSS_SELECTOR, "a.search-result-productname")

        title = link_el.text
        url = link_el.get_attribute("href")

        #Brand
        brand = element.find_element(By.CSS_SELECTOR, "span.search-result-manufacturerName").text

        #price
        price_whole = element.find_element(By.CSS_SELECTOR, "span.search-result-price > span.price-whole").text

        #Price - frac
        price_frac = element.find_element(By.CSS_SELECTOR, "span.search-result-price > span.price-fractional").text
        price = f"{price_whole} {price_frac}"
        return {
            "title": title,
            "brand": brand,
            "price": price,
            "url": url
        }
    def check_Results(self):
        no_results = self.driver.find_elements(By.CSS_SELECTOR, "div.empty-state, div.search-results-noMatches")
        if no_results:
            print("No exact matches found")
            return False
        else:
            return True
    def WaitResults(self):
        # wait for the spinner to go away, then for at least one item
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.k-loading-mask, .loading-overlay")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#searchResultsList > li.search-results-item"))) # # < #
class MotionScraper(BaseScraper):
    def get_search_url(self, query):
        return f"https://www.motionindustries.com/products/search;q={query.replace(' ', '%20')}"
    def select_result_items(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "div.item-card.root-item-card_itemCard__KhLXr")
    def parse_item(self, element) -> dict:

        #Have to fetch the price seperately because it lives in a different card container
        priceContainer = element.find_elements(By.CSS_SELECTOR, "div.item-card-price-container_price__LruJI.list-item-card-content_price__oGaOt")
        price= element.find_element(By.CSS_SELECTOR, ".product-price_price__KhAJm").text

        #URL Link

        url = element.find_element(By.CSS_SELECTOR, "a.nounderline").get_attribute("href")

        #manufacturer/brand
        title = element.find_element(By.CSS_SELECTOR, "div.OneLinkNoTx.name_title__JU8GV.item-card-details_title__90M_y.titleDecorated").text
        brand = element.find_element(By.CSS_SELECTOR, ".name_manufacturerName__WWyRd.name_hasSeparator__AeW5f").text.split(" ")[1]

        # Motion's "MPN" (their SKU) <--- do we really need to output this?
        mpn = element.find_element(By.CSS_SELECTOR, "span.name_manufacturerPartNumber__8cmLN").text

        #Weird formatting compared to ebay so we'll have to restructure

        return {"title": title, "brand": brand, "price": price, "url": url}
    def check_Results(self):
        no_results = self.driver.find_elements(By.XPATH, "//p[contains(text(), 'No results for')]")

        if no_results:
            print("No exact matches found")
            return False
        else:
            return True
    def WaitResults(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.product-list_results__a_env")))
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "ul#searchResultsList > li.search-results-item")))
