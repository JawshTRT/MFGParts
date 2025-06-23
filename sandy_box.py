import time
import csv
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# WebDriver Setup Function
def setup_driver():
    options = Options()
    # options.add_argument("--headless")  # Uncomment to run headless
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# URLs to process (eBay and Amazon)
urls = [
    "https://www.ebay.com/itm/156164210994",
    "https://www.ebay.com/itm/166427643672",
    "https://www.ebay.com/itm/174402500294",
    "https://www.ebay.com/itm/175251791120",
    "https://www.ebay.com/itm/182057708066",
    "https://www.ebay.com/itm/184411523344",
    "https://www.amazon.com/Donaldson-G160376-Original-Fvg/dp/B015YRR7O0",
    "https://www.amazon.com/Donaldson-G160587-Original-Fvg/dp/B015YRR98O",
    "https://www.amazon.com/Donaldson-M085411-MUFFLER-ROUND-STYLE/dp/B015YRHMOA",
    "https://www.amazon.com/Donaldson-M091050-Original-Muffler/dp/B015YRJ3WO",
    "https://www.amazon.com/Donaldson-M100572-Original-Muffler/dp/B015YRJI8S",
    "https://www.amazon.com/G100297-Donaldson-Original-Frg-Radial/dp/B015YRPMBK",
    "https://www.amazon.com/G150092-Donaldson-Original-Frg-Radial/dp/B015YRR3HQ",
    "https://www.amazon.com/H000275-Donaldson-Original-Inlet-Hood/dp/B015YRRUI8",
    "https://www.amazon.com/P013722-Donaldson-Original-Mounting-Band/dp/B015YRBV1K"
]

# Output CSV setup
output_file = "./product_details.csv"  # Save in current directory
with open(output_file, "w", newline="") as csvfile:
    fieldnames = ["URL", "Title", "Price"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Setup the WebDriver
    driver = setup_driver()

    for url in urls:
        driver.get(url)
        time.sleep(3)

        title = "Error"
        price = "Error"

        try:
            # Check if the URL is an eBay link
            if "ebay.com" in url:
                # Extract title using eBay's CSS selector
                try:
                    title = driver.find_element(By.CSS_SELECTOR, "h1.x-item-title__mainTitle span").text
                except Exception as title_error:
                    logging.warning(f"Error extracting title from {url}: {title_error}")

                # Extract price using eBay's CSS selector
                try:
                    price = driver.find_element(By.CSS_SELECTOR, ".x-price-primary span").text
                except Exception as price_error:
                    logging.warning(f"Error extracting price from {url}: {price_error}")

            # Check if the URL is an Amazon link
            elif "amazon.com" in url:
                # Extract title using Amazon's CSS selector
                try:
                    title = driver.find_element(By.ID, "productTitle").text.strip()
                except Exception as title_error:
                    logging.warning(f"Error extracting title from {url}: {title_error}")

                # Extract price using Amazon's CSS selector
                try:
                    whole_price = driver.find_element(By.CSS_SELECTOR, ".a-price .a-price-whole").text
                    fraction_price = driver.find_element(By.CSS_SELECTOR, ".a-price .a-price-fraction").text
                    price = f"${whole_price}.{fraction_price}"  # Combine the whole and fraction price
                except Exception as price_error:
                    logging.warning(f"Error extracting price from {url}: {price_error}")

            # Write to CSV
            writer.writerow({"URL": url, "Title": title, "Price": price})
            print(f"Extracted: {title} | {price} | {url}")

        except Exception as e:
            logging.error(f"Error processing {url}: {e}")
            writer.writerow({"URL": url, "Title": "Error", "Price": "Error"})

    # Close driver
    driver.quit()

print(f"Data extraction complete! Results saved to {output_file}")
