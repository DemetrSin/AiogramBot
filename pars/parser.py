import sqlite3

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from links import job_links
from send_mail import send_email


class BSParser:

    def __init__(self, url, http=None):
        self.url = url
        self.http = http
        self.conn = sqlite3.connect('job_listings.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_listings
        (job_title TEXT, job_url TEXT
        )''')
        self.conn.commit()

    def insert_listing(self, job_title, job_url):
        self.cursor.execute(
            "INSERT INTO job_listings (job_title, job_url) VALUES (?, ?)",
            (job_title, job_url)
        )
        self.conn.commit()

    def is_duplicate(self, job_url):
        self.cursor.execute(
            "SELECT COUNT(*) FROM job_listings WHERE job_url=?", (job_url,)
        )
        count = self.cursor.fetchone()[0]
        return count > 0

    @staticmethod
    def get_random_user_agent():
        user_agent = UserAgent()
        return user_agent.random

    def if_not_200(self):
        driver = webdriver.Chrome()
        driver.get(self.url)
        html_content = driver.page_source
        driver.quit()
        return html_content

    def fetch_job_listings(self):
        headers = {
            "User-Agent": self.get_random_user_agent()}
        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            html_content = self.if_not_200()
            return html_content

    def parse_job_listings(self, html_content):
        words = ['python', 'django', 'fastapi']
        job_info = {}
        soup = BeautifulSoup(html_content, 'html.parser')
        h2_els = soup.find_all('a')
        for el in h2_els:
            for word in words:
                if word in el.text.lower():
                    href = el.get('href')

                    if self.http:
                        job_info[' '.join(el.text.split())] = self.http + href
                    else:
                        job_info[' '.join(el.text.split())] = href

        return job_info

    @staticmethod
    def filter_listings(job_listing):
        words = ['qa', 'test', 'full-stack', 'senior', 'aqa', 'salary', 'ml']
        key_for_delete = []
        for k in job_listing:
            if set(k.lower().split()).intersection(words):
                key_for_delete.append(k)
        for key in key_for_delete:
            del job_listing[key]

        return job_listing

    def main(self):
        html_content = self.fetch_job_listings()
        if html_content:
            job_listings = self.parse_job_listings(html_content)
            filtered_listings = self.filter_listings(job_listings)
            data = []
            count = 1
            for job, href in filtered_listings.items():
                if not self.is_duplicate(href):
                    self.insert_listing(job, href)
                    data.append(f"{count}  {job} : {href}\n")
                    count += 1
            return ''.join(data)


if __name__ == '__main__':
    data = []
    for x in job_links:
        instance = BSParser(*x)
        data2 = instance.main()
        data.append(data2)
    # send_email(''.join(data))

















