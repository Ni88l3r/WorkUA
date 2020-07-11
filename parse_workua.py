import random
import sqlite3
from time import sleep

from bs4 import BeautifulSoup

import requests

from user_agent import generate_user_agent

# global variables
HOST = 'https://www.work.ua'
ROOT_PATH = '/ru/jobs/'
connection = sqlite3.connect("WorkUA.db")
cursor = connection.cursor()


def parse_links():
    page = 0
    while True:
        page += 1
        print(f'Page: {page}')
        payload = {'page': page}
        user_agent = generate_user_agent()
        headers = {'User-Agent': user_agent}
        response = requests.get(HOST + ROOT_PATH, params=payload, headers=headers)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.find_all('div', class_='card card-hover card-visited wordwrap job-link')
        if not cards:
            cards = soup.find_all('div', class_='card card-hover card-visited wordwrap job-link js-hot-block')
        if not cards:
            print('No jobs found.')
            break
        for card in cards:
            tag_a = card.find('h2').find('a')
            href = tag_a['href']
            parse_details(href)


def parse_details(href: str) -> None:
    print(f'Job link: {href}')
    user_agent = generate_user_agent()
    headers = {'User-Agent': user_agent}
    response = requests.get(HOST + href, headers=headers)
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    # Date
    date = soup.find('span', class_='text-muted')
    date = soup.find('p', class_='cut-bottom-print').text
    if 'Горячая вакансия' in date:
        date = ''
    else:
        date = date.replace('Вакансия от\xa0', '')
    # Title
    title = soup.find('div', class_='card wordwrap').find('h1').text
    # Salary
    salary = soup.find('b', class_='text-black')
    if salary is not None:
        salary = salary.text.replace('\u202f', ' ').replace('\u2009', ' ')
    else:
        salary = ''
    # Address
    address = soup.find('p', class_='text-indent add-top-sm').contents[2].strip()
    # Description
    description = soup.find('div', id='job-description').text
    print(f'{date} {title} {salary} {address}')
    cursor.execute("""INSERT INTO vacancy VALUES (?, ?, ?, ?, ?)""", (date, title, salary, address, description))
    connection.commit()
    sleep(random.randint(1, 4))


def main():
    cursor.execute('''CREATE TABLE vacancy (date text, title text, salary text, address text, description text)''')
    parse_links()
    connection.close()


if __name__ == "__main__":
    main()
