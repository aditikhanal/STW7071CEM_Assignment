import os
import time
import ujson
import schedule


import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# Delete files if present
try:
    os.remove('Authors.txt')
    os.remove('crawler_results.json')
except OSError:
    pass


def write_authors(list1, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        for i in range(0, len(list1)):
            f.write(list1[i] + '\n')

def start_crawling(crawl_link):
    start_time = time.time()
    # Initialize driver for Chrome
    web_opts = webdriver.ChromeOptions()
    web_opts.add_experimental_option('excludeSwitches', ['enable-logging'])
    web_opts.add_argument('--ignore-certificate-errors')
    web_opts.add_argument('--incognito')
    web_opts.add_argument('--headless')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(crawl_link)  # Start with the original link

    profile_links = []  # Array with pureportal profiles URL
    publication_data = []  # To store publication information for each pureportal profile
    
    try:
        # Wait until the 'Accept All Cookies' button is present and clickable
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
        )

        # Click the 'Accept All Cookies' button
        accept_button.click()

        print("Clicked the 'Accept All Cookies' button.")

    except Exception as e:
        print(f"An error occurred: {e}")

    print("Crawler has started...")
   
    page = driver.page_source
    # XML parser to parse each URL
    bs = BeautifulSoup(page, "html.parser")

    # Extracting the exact URL by splitting string into list
    for link in bs.findAll('a', class_='link person'):
        url = str(link)[str(link).find('https://pureportal.coventry.ac.uk/en/persons/'):].split('"')
        profile_links.append(url[0])

            
    total_links = len(profile_links)
    print("Crawler has found ", total_links, " pureportal profiles")
    write_authors(profile_links, 'Authors.txt')

    print("Scraping publication data for ", total_links, " pureportal profiles...")
    count = 1
    for profile_link in profile_links:
        print("Scraping publication data ", count, " of ", total_links, " pureportal profiles...")

        # Visit each link to get data
        time.sleep(1)
        driver.get(profile_link)
        try:
            if driver.find_elements("css selector", ".portal_link.btn-primary.btn-large"):
                element = driver.find_elements("css selector", ".portal_link.btn-primary.btn-large")
                for a in element:
                    if "research output".lower() in a.text.lower():
                        driver.execute_script("arguments[0].click();", a)
                        driver.get(driver.current_url)
                        # Get name of Author
                        name = driver.find_element("css selector", "div[class='header person-details']>h1")
                        r = requests.get(driver.current_url)
                        # Parse all the data via BeautifulSoup
                        soup = BeautifulSoup(r.content, 'html.parser')

                        # Extracting publication name, publication url, date and CU Authors
                        table = soup.find('ul', attrs={'class': 'list-results'})
                        if table is not None:
                            for row in table.findAll('div', attrs={'class': 'result-container'}):
                                pub_name = row.h3.a.text
                                pub_url = row.h3.a['href']
                                auth_name = name.text
                                date = row.find("span", class_="date")

                                data = {'name': pub_name, 'pub_url': pub_url, 'cu_author': auth_name, 'date': date.text,'author_url':profile_link}

                                print("Publication Name :", pub_name)
                                print("Publication URL :", pub_url)
                                print("Author Name :", auth_name)
                                print("Date :", date.text)
                                print("Author Url:", profile_link)
                                print("\n")
                                publication_data.append(data)
            else:
                # Get name of Author
                name = driver.find_element("css selector", "div[class='header person-details']>h1")
                resp = requests.get(profile_link)
                # Parse all the data via BeautifulSoup
                soup = BeautifulSoup(resp.content, 'html.parser')
                # Extracting publication name, publication url, date and CU Authors
                table = soup.find('div', attrs={'class': 'relation-list relation-list-publications'})
                if table is not None:
                    for row in table.findAll('div', attrs={'class': 'result-container'}):
                        auth_name = name.text
                        pub_name = row.h3.a.text
                        pub_url = row.h3.a['href']
                        date = row.find("span", class_="date")
                        data = {"name": pub_name, 'pub_url': pub_url, 'cu_author': name.text, 'date': date.text}
                        print("Publication Name :", pub_name)
                        print("Publication URL :", pub_url)
                        print("Author Name :", auth_name)
                        print("Date :", date.text)
                        print("\n")
                        publication_data.append(data)
        except Exception as err:
            print("Error : ", type(err).__name__)
            continue

        count += 1

    print("Crawler has scrapped data for ", len(publication_data), " pureportal publications")
    driver.quit()
    # Writing all the scraped results in a file with JSON format
    with open('crawler_results.json', 'w') as f:
        ujson.dump(publication_data, f)

    exec_time = format((time.time() - start_time), ".2f")
    print("Total Crawl Time : ", exec_time, " s")


crawl_link = 'https://pureportal.coventry.ac.uk/en/organisations/school-of-computing-mathematics-and-data-sciences/persons/'
start_crawling(crawl_link)

schedule.every().saturday.at("12:30").do(
    lambda: start_crawling(crawl_link)
)

while True:
    schedule.run_pending()
    time.sleep(1)