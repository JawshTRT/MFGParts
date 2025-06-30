import BaseScraper
from selenium.webdriver.common.by import By


class EbayScraper(BaseScraper):
    """
    Inherits from the BaseScraper abstract base class
    :var BaseScraper:
        Abstract base class that inherits from BaseScraper
    """

    def get_search_url(self, query: str):
        return f"https://www.ebay.com/search/sch/i.html?_nkw={query.replace(' ', '+')}"

    def select_result_items(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "ul.srp-results li.s-item")

    def parse_item(self, element):
        title = element.find_element(By.CSS_SELECTOR, "h3.s-item__title").text
        price = element.find_element(By.CSS_SELECTOR, ".s-price").text
        url = element.find_element(By.CSS_SELECTOR, "a.s-item__link").get_attribute("href")

        return {"title": title, "price": price, "url": url}


class RadwellScraper(BaseScraper):
    """
    Inherits from the BaseScraper abstract base class
    :var BaseScraper:
        Abstract base class that inherits from BaseScraper
    """

    def get_search_url(self, query):
        return (f"https://www.radwell.com/Search/Advanced?q={query.replace('', '+')}")

    def select_result_items(self):
        # Radwell uses a table of <tr> rows for results
        return self.driver.find_elements(By.CSS_SELECTOR, "table#SearchResultsGrid tbody tr")

