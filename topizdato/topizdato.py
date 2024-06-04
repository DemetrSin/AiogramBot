import re

import requests
from bs4 import BeautifulSoup
from selenium import webdriver


def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        driver = webdriver.Chrome()
        driver.get(url)
        html_content = driver.page_source
        driver.quit()
        return html_content


def make_soup(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    if soup:
        return soup


soup = make_soup(html_content=fetch_data('https://www.education.ua/courses/19489/'))


def parse_soup(soup):
    if soup:
        course_title = soup.find('h1', {'class': 'display-2', 'itemprop': 'name'}).text.strip()
        price_value = soup.find('b', {'class': 'fs-22'}).text
        company_pattern = re.compile(r'/courses/company/\d+/')
        company = soup.find('a', {'href': company_pattern}).text
        group = soup.find('span', {'class': 'glyphicon glyphicon-age-group'}).find_next_sibling('span').text
        location = soup.find('span', {'class': 'glyphicon glyphicon-location'}).find_next('a').text
        website = soup.find('span', {'class': 'glyphicon glyphicon-website'}).find_next('span').text
        contact = soup.find('span', {'class': 'glyphicon glyphicon-contact'}).find_next('span').text
        description = soup.find('div', {'itemprop': 'description'}).text.strip()

        print("Course Title:", course_title)
        print("Price Value:", price_value)
        print("Company:", company)
        print("Group:", group)
        print("Location:", location)
        print("Website:", website)
        print("Contact:", contact)
        print("Description:", description)


def links_pagination():
    links = []
    for page in range(1, 111):
        link = f'https://www.education.ua/courses/?search=&city=0&kind=0&page={page}'

        links.append(link)
    return links


def fetch_courses_links(soup):
    if soup:
        course_cards = soup.find_all('div', class_='card')
        links = []
        for card in course_cards:
            a_tag = card.find('h2')
            if a_tag:
                a_tag = a_tag.find('a')
                href = a_tag['href']
                full_href = 'https://www.education.ua/' + href
                links.append(full_href)
        return links


def total_links():
    total = []
    links = links_pagination()
    for link in links:
        soup = make_soup(html_content=fetch_data(link))
        courses_links = fetch_courses_links(soup)
        for course in courses_links:
            total.append(course)
    return total


def main():
    parse_soup(soup)


if __name__ == '__main__':
    print(len(total_links()))

