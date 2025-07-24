from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.devtools.v135.page import remove_script_to_evaluate_on_load
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Web_Class.WebScrapers import (EbayScraper, GoogleScraper, PartsRus)
import pandas as pd
import time
import inflect


def Append_Results_CSV(df: pd.DataFrame, path):
    #If the file does exist write with headers otherwise just append
    df.to_csv(path,
              mode='a',
              header=False,
              index=False)

def Driver_Init():
    """
    Initializes the selenium webdriver via chromedriver
    :return driver:
        The webdriver instance to be returned
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  #<---- Considering running headless

    #Extra arguments added to bypass bot-captchas
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=Default')
    options.add_argument("--incognito")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--start-maximized")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")

    # Selecting which search tool to use Google Chrome or Firefox, Edge, etc.
    driver = webdriver.Chrome(options=options)
    stealth(driver, vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer=
    "Intel Iris OpenGL Engine",
            fix_hairline=True)
    return driver
def ImportCSv(filename):
    """Reads the respective csv file
    :param filename:
        The name of the csv file in the workspace directory to be read
    :return search_terms:
        The list of search terms for the webscraper to search on ebay
    :return SKU:
        The list of SKUs for the webscraper
    """
    df = pd.read_csv(filename)
    # Extracting the file column full of item names
    PartNum = df['Model'].dropna().astype(str).tolist()
    Part = df['Product Type'].dropna().astype(str).tolist()
    Brand = df['Brand'].dropna().astype(str).tolist()
    SKU = df['SKU'].dropna().astype(str).tolist()
    IDs = df['ID'].dropna().astype(str).tolist()
    p = inflect.engine()

    # Creating ebay search entries
    search_terms = []
    terms = []
    for x, y, z in zip(Brand, Part, PartNum):

        # Skip parts that have a hyphenated model number
        if z == '-':
            print(f"No model number found for {x} {y} skipping this part for search")
            continue
        if x in y:  # <--- If Brand name is in the part string exclude it from the search term string to avoid search mismatching
            y = y.replace(x, '')[1:]
        if '-' in x:
            x = x.replace('-', ' ')
        try:
            if y[-1] == 's':
                y = p.singular_noun(y)
        except IndexError:
            print(f"Error printing {x, y, z}")
        search_terms.append(f"{x} {y} {z}")
        terms.append((x, y, z))  # Each entry contains a 'set' containing the brand part and part number
    return search_terms, terms, SKU, IDs
def Check_Item(Brand: str, Part: str, Num: str, Name: str) -> bool:
    """Checks the item based purely off of the name of the search result
    to see if it contains the correct part number
    :param Brand:
    The Brand name
    :param Part:
    The name of the part
    :param Num:
    The number associated with the Part
    :param Name:
    The name of the search entry to be validated"""
    name = Name.lower().replace('-', '')
    checks = [Num.lower().replace('-', ' ') in name,
              Part.lower().replace('-', ' ') in name]
    partnum = Num.lower().replace('-', '') in name or Num.lower().replace(' ', '') in name
    if Brand:  # <--- only check brand if you actually searched with one
        checks.append(Brand.lower() in name)
    return partnum
def URL_Fetcher(browser, item_query, terms):
    """
    Checks a url to determine if it is a valid item page on the URL...
    :param item_query:
        Item to be searched through ebay
    :param browser:
        The driver object to access the webpage using the URL
    :return CleanLinks:
        A list of 7 links to sift through items and their specifications
    """
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={item_query.replace(' ', '+')}"  # <--- Ebay's URL, replacing spaces with '+'s
    browser.get(ebay_url)
    wait = WebDriverWait(browser, 20)  # Waiting even longer (10 more seconds for the search results list to exit)
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "ul.srp-results")))  # <-- only shows up once ebay has rendered actual search hits
    WebDriverWait(browser, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")

    # Results are sometimes lazy loaded so scroll at least once
    browser.execute_script("window.scrollBy(0, 1000);")
    time.sleep(1)
    Link = browser.find_element(By.CSS_SELECTOR, "ul.srp-results").find_elements(By.CSS_SELECTOR, "li.s-item")
    no_match = browser.find_elements(By.XPATH, "//*[contains(text(),'No exact matches found')]")

    if no_match:
        print("No exact matches found on eBay - skipping this part")
        return 0

    CleanLinks = []
    seen_urls = set()
    print(f"{len(Link)} listings found for {item_query}")  # <---- Debug

    # Iterating through links to see if there are any invalid links and to check if any of the parts are valid
    for l in Link:
        try:
            link = l.find_element(By.CSS_SELECTOR, "a.s-item__link").get_attribute("href")
            title = l.find_element(By.CSS_SELECTOR, ".s-item__title").text
            price = l.find_element(By.CSS_SELECTOR, ".s-item__price").text
        except NoSuchElementException:
            continue
        if "/itm/" not in link:
            continue

        if link in seen_urls:
            continue
        if not Check_Item(terms[0], terms[1], terms[2], title):
            print(f"Skipping {title} missing either, {terms}")
            if l == Link[-1] and len(CleanLinks) == 0:
                return 0
            #time.sleep(1)
            # Skip listings whose title don't include all three in the name
            continue
        seen_urls.add(link)
        CleanLinks.append(l)

        # Limiting it to the first 6 links
        if len(CleanLinks) == 6:
            break

        #Checking to see if we have reached the end of the list and searched through every term

    return CleanLinks
def get_top_3_ebay(item_query, terms):
    driver = Driver_Init()

    # Storing the results from the URL_Fetcher function
    search_results = URL_Fetcher(driver, item_query, terms)

    if search_results == 0:
        print(f"No valid ebay listings for {item_query}; skipping this listing")
        driver.quit()
        return 0
    if len(search_results) == 0:
        for attempt in range(1, 3 + 1):
            print(f"Attempt {attempt}/{3}...")
            driver = Driver_Init()
            try:
                search_results = URL_Fetcher(driver, item_query, terms)
                if search_results == 0:
                    return 0
                elif len(search_results) > 0:
                    break
            except Exception as e:
                print(f"No results, retrying in {2}s...")
            time.sleep(2)

    listings = []
    # Scraping the data in each search result
    for search in search_results:

        # Fetching name
        name = search.find_element(By.CSS_SELECTOR, ".s-item__title").text

        #TODO: Enter a new exception clause to tackle varying condition tags on item listings
        try:
            cond = search.find_element(By.CSS_SELECTOR, ".s-item__subtitle").text
        except NoSuchElementException:
            cond = "Invalid Condition element"
        # Price
        price = search.find_element(By.CSS_SELECTOR, ".s-item__price").text
        # Link
        link = search.find_element(By.CSS_SELECTOR, ".s-item__link").get_attribute("href")

        # Each listing entry will use a dictionary to store the price, brand, and name
        listings.append({"name": name, "cond": cond,
                         "price": price, "link": link})

    #Close the driver
    driver.quit()
    return listings
if __name__ == "__main__":
    #Importing the CSV file
    products, terms, SKU, Ids = ImportCSv('PartsList/2015 w_Josh - Pricing.csv')

    #Creating the CSV output files
    df = pd.DataFrame(columns = ['Id', 'SKU', 'Search Query', 'Brand', 'Product Type', 'Model', 'Price'])
    df.to_csv("ResultsList/ebay_results.csv", header=True, index=False)
    df.to_csv("ResultsList/ebay_resultsToDo.csv", header=True, index=False)


    spread = []
    toSpread = []
    # Initializing scrapers with their respective terms
    Escraper = EbayScraper(headless=False, monitor_index=1, half="right")
    PartScraper = PartsRus(headless=False, monitor_index=1, half ="left")
    # Iterating through each product from the imported list
    for item, term, number, Id  in zip(products, terms, SKU, Ids):

        #Setting the terms to compare to inside the scraper
        Escraper.setBrand(term[0])
        Escraper.setPart(term[1])
        Escraper.setPartNum(term[2])

        PartScraper.setBrand(term[0])
        PartScraper.setPart(term[1])
        PartScraper.setPartNum(term[2])



        #Initializing counter variables for finding price averages
        summation, count = 0.0, 0
        results = Escraper.scrape(item, 6) # <----Scrape with the parsed string

        if len(results) == 0:
            print("No results scraping on industrial parts R us")
            results = PartScraper.scrape(item, 6)

        for result in results:
            result['SKU'] = str(number)
            # result['Id'] = str(Id)
            print(f"Partnum: {term[2]}\n")
            print(f"Name: [{result["title"]}]\n Condition: [{result['condition']}]\nPrice: [{result['price']}]\n Link: [{result['url']}\n SKU: [{result['SKU']}]")
            try:
                summation += float(result['price'][1:].replace(',', ''))
            except ValueError:
                print("Could not parse price properly taking lower portion of price")
                summation += float(result['price'][1:].replace(',', '').split(' ')[0])
            count += 1

        row = [(Id, number, item, term[0], term[1], term[2], f"${summation / float(count):.2f}" if summation != 0 else "No price listings for average")]
        if summation != 0: # <--- if the summation is equal to zero it means that there were no accurate listings found
            average = f"${summation / count:.2f}"
            print(f"Average: {average}")

        else:
            #Append listings with no average anyway so that way they are easier to align with
            toSpread.append(row)
            df1 = pd.DataFrame(row)
            Append_Results_CSV(df1, "ResultsList/ebay_resultsToDo.csv")

        spread.append(row)
        df = pd.DataFrame(row)

        Append_Results_CSV(df, "ResultsList/ebay_results.csv")  # < ------- Updating the CSV file

    # Converting to dataframe
    df = pd.DataFrame(spread)
    df.to_csv("ResultsList/ebay_results.csv", index=False)

    df1 = pd.DataFrame(toSpread)
    df1.to_csv("ResultsList/ebay_resultsToDo.csv", index=False)

    print("Saved", len(df), "rows to ResultsList/ebay_results.csv")
    print("Saved", len(df1), "rows to ebay_resultsToDo.csv")
