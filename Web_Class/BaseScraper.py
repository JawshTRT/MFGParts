from abc import ABC, abstractmethod
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Inheriting from abstract class
class BaseScraper(ABC):
    """
    Template for defining other web scrapers for other websites
    :var driver: webdriver instance
    """
    def __init__(self, Items: list[dict], headless: bool = False):
        """
        Default Constructor for BaseScraper abstract class
        :param headless:
            True by default, it determines
             whether the driver will run headless (without a window)
        """
        self.driver = self.Driver_Init(headless) # <--- Initializing the driver
        self.Items = Items

    @abstractmethod
    def get_search_url(self, query: str) -> str:
        """Build the URL to load for a given search query
        :param query: search query for the website"""
        pass

    @abstractmethod
    def select_result_items(self):
        """Return a list of WebElements pointing at each result container"""
        pass
    @abstractmethod
    def Check_Matches(self, Items: list[str]) -> bool:
        """Check to see if any of the items match the search query"""
        pass
    @abstractmethod
    def parse_item(self, element) -> dict:
        """Parse a WebElement and return a dictionary
        :param element: The WebElement to parse
        :return dict: The parsed item
        """
        pass
    def get_items(self):
        """Gets the items from the web page"""
        link = self.driver.find_element(By.CSS_SELECTOR, "ul.srp-results").find_elements(By.CSS_SELECTOR, "li.s-item")


    def Driver_Init(self, headless: bool = False):
        """
        Initializes the selenium webdriver
        :return driver: The selenium webdriver to search the internet with
        """
        options = webdriver.ChromeOptions()
        # Extra arguments added to bypass bot-captchas
        options.add_argument('--disable-extensions')
        options.add_argument('--profile-directory=Default')
        options.add_argument("--incognito")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--start-maximized")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")

        if headless:
            options.add_argument("--headless") # <-- Running without browser window
        driver = webdriver.Chrome(options=options)
        stealth(driver, vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer=
        "Intel Iris OpenGL Engine",
                fix_hairline=True)
        return driver
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

        print("Waiting for results...")
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.srp-results")))
        WebDriverWait(self.driver, 20).until(lambda d: d.execute_script("return document.querySelector('ul.srp-results')") == "complete")

        # self.driver.implicitly_wait(2) <-- A different method to wait for results to load


        elems = self.select_result_items()
        results = [self.parse_item(el) for el in elems]
        return results

    def close(self):
        self.driver.quit()


