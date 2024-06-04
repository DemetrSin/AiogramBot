import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import uuid


log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
log_file = os.path.join(log_directory, 'scraping.log')


def get_logger():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
        logging.FileHandler(log_file, mode='a'),
        logging.StreamHandler()
    ])
    logger = logging.getLogger()
    return logger


class Item:
    """
    Represents an item with its details.
    """

    def __init__(self, title, description, price, link, bonanza_id, color, size):
        """
        Initialize an Item object.

        Args:
            title (str): The title of the item.
            description (str): The description of the item.
            price (str): The price of the item.
            link (str): The URL link to the item.
            bonanza_id (str): The Bonanza ID of the item.
            color (str): The color of the item.
            size (str): The size of the item.
        """
        self.title = title
        self.description = description
        self.price = price
        self.link = link
        self.unique_key = str(uuid.uuid4())
        self.bonanza_id = bonanza_id
        self.color = color
        self.size = size


categories = [
    "https://www.bonanza.com/items/search?q[filter_category_id]=15724",
    "https://www.bonanza.com/items/search?q[filter_category_id]=1059",
    "https://www.bonanza.com/items/search?q[filter_category_id]=93427"
]


def get_driver(link):
    """
    Open a Chrome WebDriver instance and navigate to the specified link.

    Args:
        link (str): The URL to navigate to.

    Returns:
        webdriver.Chrome: The WebDriver instance.
    """
    options = webdriver.ChromeOptions()
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    return driver


def scrape_product_details(link):
    """
    Scrape product details from a given item page.

    Args:
        link (str): The URL of the item page.

    Returns:
        dict: A dictionary containing the scraped item details.
    """
    driver = get_driver(link)

    try:
        title = driver.find_element(By.TAG_NAME, 'h2').text
        price = driver.find_element(By.CLASS_NAME, 'item_price').text

        try:
            bonanza_id = driver.find_element(By.XPATH,
                                             '//th[contains(text(), "Item number")]/following-sibling::td').text
        except:
            bonanza_id = None

        try:
            color = driver.find_element(By.XPATH, '//th[contains(text(), "Color")]/following-sibling::td').text
        except:
            color = None

        try:
            size = driver.find_element(By.XPATH, '//th[contains(text(),"Size")]/following-sibling::td').text
        except:
            size = None

        html_description_element = driver.find_element(By.CLASS_NAME, 'html_description')
        if html_description_element:
            iframe_src = html_description_element.find_element(By.TAG_NAME, 'iframe').get_attribute('src')
            driver.get(iframe_src)
            description = driver.find_element(By.TAG_NAME, 'body').text
        else:
            plain_text_description_element = driver.find_element(By.CLASS_NAME, 'plain_text_description')
            description = plain_text_description_element.text

        item = Item(title, description, price, link, bonanza_id, color, size)
        return item.__dict__
    except Exception as e:
        logger = get_logger()
        logger.error(f"Error scraping item from link {link}: {e}")
        return None
    finally:
        driver.quit()


def main():
    """
    Main function to scrape items from Bonanza categories and save the details to a CSV file.
    """
    items = []
    logger = get_logger()

    for category_url in categories:
        driver = get_driver(category_url)

        product_elements = driver.find_elements(By.CLASS_NAME, 'item_title_and_price')
        for product in product_elements[:5]:
            try:
                link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
                item_details = scrape_product_details(link)
                # logger.info(item_details)
                if item_details:
                    items.append(item_details)
            except Exception as e:
                logger.error(f"Error scraping item from link {link}: {e}")

        driver.quit()

    logger.info(f"Total items scraped: {len(items)}")

    if items:
        df = pd.DataFrame(items)
        df.to_csv('out.csv', index=False)
    else:
        logger.info("No items were scraped.")


if __name__ == '__main__':
    main()
