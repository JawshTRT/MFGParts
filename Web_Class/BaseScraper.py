from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement


#Inheriting from abstract class
class BaseScraper(ABC):
    """
    Template for defining other web scrapers for other websites
    """
    def __init__(self, headless: bool = True):
        """
        Default
        :param headless:
            True by default, it determines
             whether the driver will run headless (without window)
        """
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")

        @abstractmethod
        def get_search_url(self, query: str) -> str:
            """Build the URL to load for a given search query"""
            pass

        @abstractmethod
        def select_result_items(self):
            """Return a list of WebElements pointing at each result container"""
            pass

        @abstractmethod
        def parse_item(self, element) -> dict:
            """Parse a WebElement and return a dictionary

            """
            pass

        def scrape(self, search_query: str, n: int = 3) -> list[dict]:
            """

            :param search_query:
                The item to search for
            :param n:
                Determines the number of results to grab from the search listings
            :return results:
            A list of dictionaries containing the search results
            """
            url = self.get_search_url(search_query)
            self.driver.get(url)

            self.driver.implicitly_wait(2)

            elems = self.select_result_items()
            results = [self.parse_item(el) for el in elems]
            return results

        def close(self):
            self.driver.quit()


