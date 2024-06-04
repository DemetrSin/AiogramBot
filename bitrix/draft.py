from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import uuid


class Item:
    def __init__(self, title, description, price, link, bonanza_id, color, size):
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

options = webdriver.ChromeOptions()
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')


def scrape_product_details(link):
    driver = webdriver.Chrome(options=options)
    driver.get(link)

    try:
        title = driver.find_element(By.TAG_NAME, 'h2').text
        price = driver.find_element(By.CLASS_NAME, 'item_price').text

        try:
            bonanza_id = driver.find_element(By.XPATH, '//th[text()="Item number:"]/following-sibling::td').text
        except:
            bonanza_id = None

        try:
            color = driver.find_element(By.XPATH, '//th[text()="Color:"]/following-sibling::td').text
        except:
            color = None

        try:
            size = driver.find_element(By.XPATH, '//th[text()="Size:"]/following-sibling::td').text
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
        print(f"Error scraping item from link {link}: {e}")
        return None
    finally:
        driver.quit()


items = []

for category_url in categories:
    driver = webdriver.Chrome(options=options)
    driver.get(category_url)

    product_elements = driver.find_elements(By.CLASS_NAME, 'item_title_and_price')
    for product in product_elements[:5]:
        try:
            link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
            item_details = scrape_product_details(link)
            if item_details:
                items.append(item_details)
        except Exception as e:
            print(f"Error scraping item from link {link}: {e}")

    driver.quit()

print(f"Total items scraped: {len(items)}")

if items:
    df = pd.DataFrame(items)
    df.to_csv('out.csv', index=False)
else:
    print("No items were scraped.")


# if items:
#     with open('out.csv', mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.DictWriter(file, fieldnames=items[0].keys())
#         writer.writeheader()
#         for item in items:
#             writer.writerow(item)
# else:
#     print("No items were scraped.")