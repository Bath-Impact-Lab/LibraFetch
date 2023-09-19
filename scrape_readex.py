import os
import shutil
import ssl
import time
import tkinter
import tkinter.constants
import tkinter.filedialog
import random
import re
from urllib.request import urlretrieve

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select  # Allows button clicks

import pyautogui
from dotenv import load_dotenv, find_dotenv

def askDialog():
    return tkinter.filedialog.askdirectory()


def inp(text):
    return input(text)


ssl._create_default_https_context = ssl._create_unverified_context

output_directory = "C:/Users/mrt64/OneDrive - University of Bath/Student-Meetings-Notes/Alice/scraped_newsbank"
download_directory = "C:/Users/mrt64/Downloads"

def download_this_page(download_dir, output_dir, driver, good_soup):

    data = driver.execute_script("return document.documentElement.outerHTML")
    print("Extracting documents")
    good_soup = BeautifulSoup(data, "lxml")

    # Parse each page of search results until there is no next page
    search_results_this_page = good_soup.find_all("div", "search-hits")

    # get all classes called search-hit
    search_hits = search_results_this_page[0].find_all("div", "search-hit")

    # for each result
    for search_hit in search_hits:

        # <div class="search-hit__hit-number">       1      </div>
        result_number = int( search_hit.find("div", "search-hit__hit-number").text.replace(' ', '') )

        # <div class="search-hit__title">
        #         <a href="/apps/readex/doc?p=HN-SARDM&amp;sort=YMD_date%3AA&amp;fld-nav-0=YMD_date&amp;val-nav-0=1940%20-%201999&amp;f=advanced&amp;val-base-0=white&amp;fld-base-0=alltext&amp;bln-base-1=and&amp;val-base-1=native&amp;fld-base-1=alltext&amp;bln-base-2=and&amp;val-base-2=bantu&amp;fld-base-2=alltext&amp;bln-base-3=and&amp;val-base-3=coloured&amp;fld-base-3=alltext&amp;docref=image/v2%3A135DEF57238F5FC5%40EANX-15EDB9864F2C0C68%402429634-15ED19F4ED007648%4011-15ED19F4ED007648%40&amp;firsthit=yes" title="Go to document viewer for News Article">News Article</a>
        #         <span class="search-hit__title-meta">
        #           page 12
        #           </span>

        result_source_page_number = search_hit.find("span", "search-hit__title-meta").text
        result_source_page_number = re.search(r"page (\d+)", result_source_page_number).group()


        # </div>
        #     <div class="search-hit__collection">

        document_info = search_hit.find("div", "search-hit__collection").find("table").find_all("td")

        #       <table>
        #               <tbody><tr class="meta-field__display_date">
        #                                 <td class="meta__label">Date</td>
        #             <td class="meta__value">January 5, 1940                          </td>
        #                   </tr>

        result_source_date = document_info[1].text
        result_source_date = str(result_source_date).strip()
            #search_hit.find("td", "meta__value").text)

        #               <tr class="meta-field__source">
        #                                 <td class="meta__label">Source</td>
        #             <td class="meta__value"><div class="search-hit-source">
        #               <span class="current-title">
        #                 Rand Daily Mail
        #               </span>

        result_source_news_title = str(document_info[3].text).strip()

            #search_hit.find("span", "current-title").text)

        #                 <span class="published-as">
        #                   (published as
        #                   <span class="original-title">RAND DAILY MAIL</span>)
        #                 </span>
        #               </div>                          </td>
        #                   </tr>
        #               <tr class="meta-field__publication_location">
        #                                 <td class="meta__label">Place(s) of Publication</td>
        #             <td class="meta__value">Johannesburg, South Africa                          </td>
        #                   </tr>

        result_source_publication_location = str(document_info[5].text).strip()
        result_source_publication_location = re.search(r"(\w+)\n", result_source_publication_location).group()
        #search_hit.find("td", "meta__value").text

        #           </tbody></table>
        #           </div>

        title = search_hit.find("class", "search-hit__title")

        # open document viewer
        # # <div class="search-hit__title">
        #         #         <a href="/apps/readex/doc?p=HN-SARDM&amp;sort=YMD_date%3AA&amp;fld-nav-0=YMD_date&amp;val-nav-0=1940%20-%201999&amp;f=advanced&amp;val-base-0=white&amp;fld-base-0=alltext&amp;bln-base-1=and&amp;val-base-1=native&amp;fld-base-1=alltext&amp;bln-base-2=and&amp;val-base-2=bantu&amp;fld-base-2=alltext&amp;bln-base-3=and&amp;val-base-3=coloured&amp;fld-base-3=alltext&amp;docref=image/v2%3A135DEF57238F5FC5%40EANX-15EDB9864F2C0C68%402429634-15ED19F4ED007648%4011-15ED19F4ED007648%40&amp;firsthit=yes" title="Go to document viewer for News Article">News Article</a>
        #

        # download document

        # move files in download_directory to output_directory
        for root, dirs, files in os.walk(download_dir):
            for f in files:
                # prefix downloaded file with page_link_counter so that they are in order
                shutil.move(os.path.join(root, f), output_dir + '/' + str(page_link_counter) + '_' + f)


def readex_image_scrape(url, download_dir, output_dir):
    try:
        webdriver_options = Options()
        #webdriver_options.add_argument('--headless')
        webdriver_options.add_argument('--no-sandbox')
        webdriver_options.add_argument('--disable-dev-shm-usage')
        folder_path_to_store_session = "C:/Users/mrt64/AppData/Local/Google/Chrome/User Data"
        webdriver_options.add_argument("--user-data-dir=" + folder_path_to_store_session)

        # driver = webdriver.Chrome(ChromeDriverManager().install(), options=webdriver_options) #chrome_options is deprecated

        s = Service('chromedriver/chromedriver')
        driver = webdriver.Chrome(service=s, options=webdriver_options)

        #driver.maximize_window()
        driver.set_window_size(1400, 1000)

        driver.get(url)
#        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")  # Scroll to the bottom of the page
        time.sleep(3)  # Wait 4 seconds for all the images to load
        data = driver.execute_script("return document.documentElement.outerHTML")
        print("Extracting documents")
        good_soup = BeautifulSoup(data, "lxml")

        # Check if me need to login find id  = btnLoginReg
        login_container = good_soup.find_all(id="btnLoginReg") # good_soup.find_all('id', {'id': 'username'})
        if login_container:
            if os.getenv("BRITISH_LIBRARY_USERNAME") is None:
                load_dotenv(find_dotenv(raise_error_if_not_found=True))
            print("Signing in as:" + os.getenv("BRITISH_LIBRARY_USERNAME"))
            USERNAME = os.getenv("BRITISH_LIBRARY_USERNAME")
            PASSWORD = os.getenv("BRITISH_LIBRARY_PASSWORD")

            # fill out username and password
            username = driver.find_element(By.ID, "username")
            username.send_keys(USERNAME)
            password = driver.find_element(By.ID, "password")
            password.send_keys(PASSWORD)
            # click login button
            login_button = driver.find_element(By.ID, "btnLoginReg")
            login_button.click()
            time.sleep(3)

        good_soup = BeautifulSoup(data, "lxml")

        expected_download_count = int( driver.find_element(By.CLASS_NAME, "search-hit__result-details__total").text.replace(',', '') )

        download_count = 0

        download_count += download_this_page(download_dir, output_dir, driver, good_soup)

        # find a tag with title = "Go to next page"
        is_there_a_next_page = driver.find_elements(By.CSS_SELECTOR, 'a[title="Go to next page"]')

        while is_there_a_next_page:
            # click next page
            next_page_link = driver.find_element(By.CSS_SELECTOR, 'a[title="Go to next page"]')
            next_page_link.click()
            time.sleep(15)

            download_count += download_this_page(download_dir, output_dir, driver, good_soup)
            # check if there is a next page
            is_there_a_next_page = driver.find_elements(By.CSS_SELECTOR, 'a[title="Go to next page"]')

        driver.close()

        return download_count

    except Exception as e:
        print(e)

'''
    if os.path.exists(output_directory + '/' + volume + '/' + paper):
        # directory already exists
        print(f" SKIPPING -  Directory already exists: {output_directory + '/' + volume + '/' + paper}")
    else:
        os.makedirs(output_directory + '/' + volume + '/' + paper)

        document_count = readex_image_scrape(scrape_this_url, download_directory, output_directory + '/' + volume + '/' + paper )
        time.sleep(2)  #let all downloads finish
        downloaded_count = len([name for name in os.listdir(output_directory + '/' + volume + '/' + paper) if os.path.isfile(name)])

        print(f"  Downloaded: {downloaded_count}")
        print(f"  Expected: {document_count}")

        if downloaded_count != document_count:
            print(f" WARNING! Downloaded count does not match expected count.  Expected: {document_count}  Downloaded: {downloaded_count}")

        # move files in download_directory to output_directory
        for root, dirs, files in os.walk(download_directory):
            for f in files:
                shutil.move(os.path.join(root, f), output_directory + '/' + volume + '/' + paper + '/' + f)
'''




scrape_this_url = "https://eresources.remote.bl.uk:2159/apps/readex/results?p=HN-SARDM&sort=YMD_date%3AA&fld-nav-0=YMD_date&val-nav-0=1940%20-%201999&f=advanced&val-base-0=white&fld-base-0=alltext&bln-base-1=and&val-base-1=native&fld-base-1=alltext&bln-base-2=and&val-base-2=bantu&fld-base-2=alltext&bln-base-3=and&val-base-3=coloured&fld-base-3=alltext"
#scrape_this_url = "https://eresources.remote.bl.uk:2159/apps/news/results?sort=YMD_date%3AD&p=WORLDNEWS&t=pubname%3A16ED7D43CFB7D6F4%21Sunday%2BTimes&maxresults=20&f=advanced&val-base-0=white&fld-base-0=alltext&bln-base-1=and&val-base-1=native&fld-base-1=alltext&bln-base-2=and&val-base-2=coloured&fld-base-2=alltext&bln-base-3=and&val-base-3=bantu&fld-base-3=alltext&fld-nav-1=YMD_date&val-nav-1=1940%20-%201999"

#test url
scrape_this_url = "https://eresources.remote.bl.uk:2159/apps/readex/results?page=2&p=HN-SARDM&t=year%3A1955%211955&f=advanced&sort=YMD_date%3AA&val-base-0=white&fld-base-0=alltext&bln-base-1=and&val-base-1=toothpaste&fld-base-1=alltext&bln-base-2=and&val-base-2=bantu&fld-base-2=alltext&bln-base-3=and&val-base-3=coloured&fld-base-3=alltext"



print("starting to scrape...")


# delete all files in download_directory
for root, dirs, files in os.walk(download_directory):
    for f in files:
        os.unlink(os.path.join(root, f))


print(f"  URL: {scrape_this_url}")

readex_image_scrape(scrape_this_url, download_directory, output_directory)

print("Scraping complete.")
#    restartScrape = inp("Keep scraping? ('y' for yes or 'n' for no) ")
#    if restartScrape == "n":
#        print("Scraping ended.")
#        break
