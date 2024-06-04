from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import time
import uuid
import requests


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


def solve_captcha(site_key, url):
    API_KEY = 'cdf1820120b929fbeba90f7faf2b7a35'
    s = requests.Session()
    captcha_id = s.post("http://2captcha.com/in.php",
                        data={'key': API_KEY, 'method': 'userrecaptcha', 'googlekey': site_key,
                              'pageurl': url}).text.split('|')[1]
    print(f"Solving CAPTCHA: {captcha_id}")
    recaptcha_answer = s.get(f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}").text
    while 'CAPCHA_NOT_READY' in recaptcha_answer:
        time.sleep(5)
        recaptcha_answer = s.get(f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}").text
    recaptcha_answer = recaptcha_answer.split('|')[1]
    return recaptcha_answer


def handle_captcha(driver):
    site_key = driver.find_element(By.CLASS_NAME, 'g-recaptcha').get_attribute('data-sitekey')
    url = driver.current_url
    captcha_response = solve_captcha(site_key, url)
    driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML='{captcha_response}';")
    driver.find_element(By.ID, 'recaptcha-demo-submit').click()


categories = [
    "https://www.bonanza.com/items/search?q[filter_category_id]=15724",
    "https://www.bonanza.com/items/search?q[filter_category_id]=1059",
    "https://www.bonanza.com/items/search?q[filter_category_id]=93427"
]

driver = webdriver.Chrome()

items = []

for category_url in categories:
    driver.get(category_url)
    time.sleep(5)
    product_elements = driver.find_elements(By.CLASS_NAME, 'item_title_and_price')
    print(f"Found {len(product_elements)} products in category {category_url}")

    for i, product in enumerate(product_elements[:5]):
        try:
            link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
            driver.get(link)
            time.sleep(5)
            handle_captcha(driver)

            # if "captcha" in driver.current_url:
            #     handle_captcha(driver)

            title = driver.find_element(By.TAG_NAME, 'h1').text
            description = driver.find_element(By.CLASS_NAME, 'item_description').text
            price = driver.find_element(By.CLASS_NAME, 'item_price').text
            bonanza_id = driver.find_element(By.XPATH, '//th[text()="Item number:"]/following-sibling::td').text
            color = driver.find_element(By.XPATH, '//th[text()="Color:"]/following-sibling::td').text
            size = driver.find_element(By.XPATH, '//th[text()="Size:"]/following-sibling::td').text

            item = Item(title, description, price, link, bonanza_id, color, size)
            items.append(item.__dict__)
            print(f"Scraped item {i + 1} in category {category_url}: {title}")
        except Exception as e:
            print(f"Error scraping item {i + 1} in category {category_url}: {e}")

driver.quit()

print(f"Total items scraped: {len(items)}")
if items:
    with open('out.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)
else:
    print("No items were scraped.")
