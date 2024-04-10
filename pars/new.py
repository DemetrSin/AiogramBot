import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


async def navigate_and_click(url, title):
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//h2[contains(text(), '{title}')]")))
        button.click()
        await asyncio.sleep(2)
        return driver.current_url
    finally:
        driver.quit()


async def main():
    url = "https://robota.ua/ru/zapros/junior-python-developer-remote/ukraine"
    titles = [
        'Strong junior data scientist',
        'Data analyst',
        'Python програміст'
    ]
    results = []
    for title in titles:
        link = await navigate_and_click(url, title)
        results.append((title, link))
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
