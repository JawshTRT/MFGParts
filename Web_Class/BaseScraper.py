from abc import ABC, abstractmethod
from selenium import webdriver
from selenium_stealth import stealth


# Inheriting from abstract class
class BaseScraper(ABC):
    """
    This is an abstract base class that defines the interface or template to create other website classes
    :var driver: webdriver instance
    """
    def __init__(self, terms: list[str], headless: bool = False):
        """
        Default Constructor for BaseScraper abstract class
        :param headless:
            True by default, it determines
             whether the driver will run headless (without a window)
        :param terms:
            The Brand, Part, and Part number of the item being searched for
        """
        self.driver = self.Driver_Init(headless) # <--- Initializing the driver
        self.Brand = terms[0]
        self.Part = terms[1]
        self.PartNum = terms[2]
    @abstractmethod
    def get_search_url(self, query: str) -> str:
        """Build the URL to load for a given search query
        :param query: search query for the website"""
        pass
    @abstractmethod
    def select_result_items(self):
        """Return a list of WebElements pointing at each result container"""
        pass
    def Check_Matches(self, title, brand, part, num) -> bool:
        """Check to see if any of the items match the search query
        :param title: The title of the item to compare with
        :param Items: The list of items to check

        :param brand: The brand of the items from the search query

        :param num: The part model of the items from the search query

        :param part: The part name of the items from the search query

        :returns: True if the item is a match, False otherwise
        """
        newTitle = title.lower().replace('-', '')  # <-- Removing hyphens from string
        name = brand.lower().replace('-', '')
        part = part.lower().replace('-', '')
        partnumSpace = num.lower().replace(' ', '')
        partnumHyphen = num.lower().replace('-', '')
        if partnumHyphen in newTitle or partnumHyphen in newTitle:
            return True
        else:
            print(f"Skipping {title} does not contain {num}")
            return False
    @abstractmethod
    def parse_item(self, element) -> dict:
        """Parse a WebElement and return a dictionary
        :param element: The WebElement to parse
        :return dict: The parsed item
        """
        pass
    def get_items(self, n: int):
        """Gets the items from the web page, handles if no results were fetched properly
        :param n: The number of times to retry searching for an item
        :return link: The list of webelements that contain each search result
        :returns An empty list If no exact matches were found:"""
        link = self.select_result_items()
        # Checking if there are no matches pulled first
        if len(link) == 0:
            for attempt in range(0, n+1):
                print(f"Couldn't find results for {attempt}/{n} retrying")
                self.driver.quit()
                self.driver = self.Driver_Init(headless=True)
                link = self.select_result_items()

                #Checking if zero exact matches were found
                if not self.check_Results():
                    return []
                #Checking if results were pulled
                elif len(link) > 0:
                    print(f"Found {len(link)} results for {attempt}/{n}")
                    return link
        else:
            # Results pulled
            return link
    @abstractmethod
    def check_Results(self) -> bool:
        """Checks to see if the web page spits out '0 exact matches found'
        :returns: False if the web page spits out '0 exact matches found,
        True otherwise"""
    @abstractmethod
    def WaitResults(self):
        """Waits for the web page to finish loading the results based on the selector tag
        """
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
        prefs = {"profile.managed_default_content_settings.images": 2, 'disk-cache-size': 4096}
        options.add_experimental_option('prefs', prefs)
        if headless:
            options.add_argument("--headless") # <-- Running without browser window
        driver = webdriver.Chrome(options=options)
        stealth(driver, vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer=
        "Intel Iris OpenGL Engine",
                fix_hairline=True)
        driver.delete_all_cookies() # <--- Deleting the cookie monsters
        return driver
    def scrape(self, search_query: str, n: int = 3) -> list[dict]:
        """
        This is where most of the magic happens, where the actual scraping is done
        :param search_query:
            The search query represents the item to search for
        :param n:
            Determines the number of results to grab from each successful search listing
        :return CleanResults: A list of dictionaries containing the search results
        :returns: A list of dictionaries containing the search results
        """
        url = self.get_search_url(search_query)
        self.driver.get(url)
        noresults = []
        print("Waiting for results...")
        self.WaitResults()
        # self.driver.implicitly_wait(2) <-- A different method to wait for results to load
        #items = self.get_items(3)
        # First check if there are any results
        if not self.check_Results():
            return []
        else:
            #Then check if any of the results are fetched
            items = self.get_items(3)
            # If items == 0 it means that there were no exact matches
            if not items:
                return []
            else:
                # Lastly, check if the results are a match, they first must be parsed into pieces and into list of dictionary
                results = [self.parse_item(item) for item in items]

        CleanResults = []
        #Checking if the search title matches what we want
        for result in results:
            if self.Check_Matches(result['title'], self.Brand, self.Part, self.PartNum):
                CleanResults.append(result)
            else:
                # Add to list to search on another site
                noresults.append(result)

        # If there were no results appended to clean results then we need to skip the part and scrape on a different site
        if len(CleanResults) == 0:
            return []
        else:
            return CleanResults[:n] # < -- returning the first 'n' clean results


