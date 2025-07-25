from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Web_Class.BaseScraper import BaseScraper
from selenium.webdriver.common.by import By
import time
class EbayScraper(BaseScraper):
    """
    Inherits from the BaseScraper abstract base class
    :var BaseScraper:
        Abstract base class that inherits from BaseScraper
    """
    def get_search_url(self, query: str):
        return f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}"
    def select_result_items(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, "ul.srp-results").find_elements(By.CSS_SELECTOR, "li.s-item")
        except NoSuchElementException:
            print("No listings could be found")
            return []
    def parse_item(self, element):
        title = element.find_element(By.CSS_SELECTOR, ".s-item__title").text
        price = element.find_element(By.CSS_SELECTOR, ".s-item__price").text
        try:
            float(price[1:].replace(',', ''))
        except ValueError:
            newprice = ''
            # Going through the price to see if it is a parsable number
            for el in price:
                if el.isnumeric():
                    newprice += el
            # If it is not parsable just return 0
            if not newprice.isnumeric():
                print("Price is not a parsable number")
                price = '$0'
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
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.srp-results")))
    def check_Results(self):
        no_match = self.driver.find_elements(By.XPATH,"//*[contains(text(), 'No exact matches found')]")
        if no_match:
            print("No exact matches found")
            return False
        else:
            return True
class RadwellScraper(BaseScraper):#< -- Bot captchas
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
        rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#ResultGrid .k-grid-content tr")))#< -- Bot captchas#< -- Bot captchas#< -- Bot captchas
class GraingerScraper(BaseScraper):#< -- Bot captchas
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
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#searchResultsList > li.search-results-item"))) # # < # # <
class MotionScraper(BaseScraper):
    def get_search_url(self, query):
        return f"https://www.motionindustries.com/products/search;q={query.replace(' ', '%20')}"
    def select_result_items(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "div.item-card.root-item-card_itemCard__KhLXr")
    def parse_item(self, element) -> dict:

        #Have to fetch the price seperately because it lives in a different card container
        priceContainer = element.find_elements(By.CSS_SELECTOR, "div.item-card-price-container_price__LruJI.list-item-card-content_price__oGaOt")
        try:
            price= element.find_element(By.CSS_SELECTOR, ".product-price_price__KhAJm").text
        except NoSuchElementException:
            print("No price found or quote required")
            price = "0"

        #URL Link

        url = element.find_element(By.CSS_SELECTOR, "a.nounderline").get_attribute("href")

        #manufacturer/brand
        title = element.find_element(By.CSS_SELECTOR, "div.OneLinkNoTx.name_title__JU8GV.item-card-details_title__90M_y.titleDecorated").text
        brand = element.find_element(By.CSS_SELECTOR, ".name_manufacturerName__WWyRd.name_hasSeparator__AeW5f").text.split(" ")[1]

        # Motion's "MPN" (their SKU) <--- do we really need to output this?
        mpn = element.find_element(By.CSS_SELECTOR, "span.name_manufacturerPartNumber__8cmLN").text

        #Weird formatting compared to ebay so we'll have to restructure

        return {"title": title, "brand": brand, "price": price, "url": url, "condition": "new"}# <---Motion industries is a manufacturer so their listings are all brand new
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
class MScraper(BaseScraper):
    def get_search_url(self, query):
        return f"https://www.mscdirect.com/browse/tn?rd=k&searchterm={query.replace(' ', '+')}"
    def select_result_items(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "div.flex.flex-col.md:flex-row.gap-2.justify-between ")
    def parse_item(self, element) -> dict:
        # The infocard contains the product type, dimensions, and manufacturer/Brand
        infocard = element.find_elements(By.CSS_SELECTOR, "div.tn-product-title-wrapper.w-full.md:pr-4.hover:underline.tnview-title-container.flex.flex-col.gap-1")

        brand = infocard.find_element(By.CSS_SELECTOR, "p.font-bold.uppercase.text-xs.hover:underline").text
        title = infocard.find_element(By.CSS_SELECTOR, "p.font-bold.text-sm.overflow-hidden.line-clamp").text
        url = infocard.find_element(By.CSS_SELECTOR, "a.font-bold.uppercase.text-xs.hover:underline").get_attribute("href")

        # The price is inside a completely seperate card wrapper
        pricecard = element.find_element(By.CSS_SELECTOR, "div.pt-3.px-3 pb-2.border-b-1 flex.items-center w-full.justify-between.new-search-item-top-border ")
        price = pricecard.find_element(By.CSS_SELECTOR, "p.text-xl.leading-7.font-bold.whitespace-nowrap").text

        return {"brand": brand, "title": title, "price": price, "url": url}
    def check_Results(self):
        no_results = self.driver.find_elements(By.XPATH, "//*[@id='main']/div[1]/div/div[1]/div/div/div[1]/text()")
        if no_results:
            return True
        else:
            return False
    def WaitResults(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.product-list_results__a_env")))
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.flex.p-3")))
class GoogleScraper(BaseScraper):

    def get_search_url(self, query):
        return f"https://www.google.com/search?tbm=shop&q={query.replace(" ", "+")}"

    def select_result_items(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "div.njFjte")

    def parse_item(self, element) -> dict:

        title = element.find_element(By.CSS_SELECTOR, "div.gkQHve.SsM98d.RmEs5b").text

        price = element.find_element(By.CSS_SELECTOR, "div.lmQWe").text

        url = element.find_element(By.CSS_SELECTOR, "div.VeBrne").get_attribute("src")

        merchant = element.find_element(By.CSS_SELECTOR, "span.WJMUdc.rw5ecc").text

        return {"title": title, "price": price, "url": url, "condition": "New", "brand": merchant}

    def check_Results(self):
        no_match = self.driver.find_element(By.CSS_SELECTOR, "div.sh-np__message")
        if no_match:
            return True
        else:
            return False

    def WaitResults(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sh-dgr__grid-result, div.sh-dlr__list-result")))
class PartsRus(BaseScraper):
    def get_search_url(self, query):
        return f"https://industrialpartsrus.com/?srsltid=AfmBOoq_-k_U460E_UWtf7jdQpyCNMFA4c-HnMJ94uAB2u8oOM_1Q4du#fa57/fullscreen/m=or&q={query.replace(' ', '+').replace('/', '%2F')}"
    def select_result_items(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "div.dfd-card.dfd-card-preset-product.dfd-card-type-product ")
    def parse_item(self, element) -> dict:
        price = element.find_element(By.CSS_SELECTOR, "span.dfd-card-price").text
        title = element.find_element(By.CSS_SELECTOR, "div.dfd-card-title").text
        url = element.find_element(By.CSS_SELECTOR, "a.dfd-card-link").get_attribute("href")
        brand = "N/A"
        condition = "Used"

        return {"price": price, "title": title, "condition": condition, "brand": brand, "url": url}
    def check_Results(self):
        no_match = self.driver.find_elements(By.XPATH, '//*[@id="dfd-tabs-j7uqz"]/div[2]/div/div[1]')

        if no_match:
            return False
        else:
            return True
    def WaitResults(self):

        # 1) Wait for the results container to appear
        wait = WebDriverWait(self.driver, 30)
        container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.dfd-content[id^='df-hook-results']")))

        # 2) now wait until at least one product card is inside it
        wait.until(lambda d: len(container.find_elements(By.CSS_SELECTOR, "div.dfd-card.dfd-card-preset-product.dfd-card-type-product")) > 0)

        last_height = self.driver.execute_script("return arguments[0].scrollHeight", container)
        for _ in range(10): # Should only scroll for the first 10 times to a avoid a timeout error

            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(0.3)

            new_height = self.driver.execute_script("return arguments[0].scrollHeight", container)
            # Scrolling to the bottom of the web page or at least until the max iterations

            if new_height == last_height:
                # Break out if the new scroll height is the same of the last meaning we couldn't scroll any further
                break
            last_height = new_height
    def ApplyFilter(self, brand: str):
        try:
            # Trying to look for the checkbox or label that contains the brand text:
            facet = self.driver.find_element(By.CSS_SELECTOR, "div.dfd-facet-content.dfd-facet-type-term.dfd-facet-layout-list")

            options = facet.find_elements(By.CSS_SELECTOR, "label, li, button")

            for opt in options:
                # Search for the option whose text contains the brand
                text = opt.text.strip().lower()

                #If the brand name is found inside the text
                if brand.lower() in text:
                    # scroll into view & click
                    self.driver.execute_script("arguments[0].scrollIntoView()", opt)
                    opt.click()
                    #waiting for the page to reload with filtered results
                    WebDriverWait(self.driver, 10).until(EC.staleness_of(opt))
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.dfd-content[id^='df-hook-results']")))
                    return
        except NoSuchElementException:
            # Either the facet container was there or there were no options
            print("No filter for brand located")
            pass






