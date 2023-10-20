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
from webdriver_manager.chrome import ChromeDriverManager
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

output_directory = 'C:/Users/info/OneDrive/Documents/ART-AI/OneDrive/OneDrive - University of Bath/Student-Meetings-Notes/Alice/scrapped_newsbank/Newspaper-apartheid+native-1940-99'
download_directory = "C:/Users/info/Downloads"


def download_this_page(download_dir, output_dir, driver, good_soup):

    data = driver.execute_script("return document.documentElement.outerHTML")
    print("Extracting documents")
    good_soup = BeautifulSoup(data, "lxml")

    # Parse each page of search results until there is no next page
    search_results_this_page = good_soup.find("div", "search-hits")

    # get all classes called search-hit
    search_hits = search_results_this_page.find_all('article')
    documents_parsed = 0
    # for each result
    for search_hit in search_hits:

        documents_parsed += 1

        time.sleep(1)

        # <article id="search-hits__hit--21" class="search-hits__hit search-hits__hit--image" data-docref="image/v2:16ED7D43CFB7D6F4@WHNPX-16F7CD2912BEC092@2442607-16F7CE495CFFF6AF@14-16F7CE495CFFF6AF@" data-pbi="16ED7D43CFB7D6F4">
        # ... <div class="search-hit-extended-preview-button__wrapper"><button data-hit-id="search-hits__hit--21" class="search-hit-extended-preview-button"><svg width="20px" height="14px" viewBox="0 0 20 14" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">


        # search-hits__hit--21
        # invalid literal for int() with base 10: '\n\n\n\nGotothedocumentviewerforSundayTimes:Page33\n\n\nMay171998\n\n\n\nSundayTimes\n\n\n\nJohannesburgSouthAfrica\n\nPage33\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nPreview\n\n\n\nArticlePreview×\n\nViewDocume
        # regex = re.compile('search-hits__hit--.*')
        #soup.find_all("div", {"class": regex})
        #tmp_result = search_hit.find("article", {"id": regex}).text
        #tmp_result = search_hit.find(id=regex).text

        tmp_result = search_hit.attrs['id']

        #tmp_result = search_hit.__getattribute__('id')
        result_number = int(tmp_result.replace('search-hits__hit--', '').replace(' ', '').replace(',', ''))

        # check if we have already downloaded a file starting with this result_number
        skip_this_result = False
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                if f.startswith(str(result_number).zfill(4) + '_'):
                    # file already exists
                    print(f" SKIPPING -  File already exists: {f}")
                    skip_this_result = True
                    continue

        if skip_this_result:
            continue

        #

        # clear download directory
        for root, dirs, files in os.walk(download_dir):
            for f in files:
                os.unlink(os.path.join(root, f))

        # open document viewer
        # <a href="/apps/news/document-view?p=WORLDNEWS&amp;t ... "><span class="element-invisible">Go to the document viewer for </span>Sunday Times: Page 15</a>

        regex = re.compile('.*Go to the document viewer for.*')
        document_url = search_hit.find('a', {'title': regex})['href']
        document_url = "https://eresources.remote.bl.uk:2159" + document_url

        # open document viewer
        driver.get(document_url)

        time.sleep(2)

        pyautogui.FAILSAFE = False
        pyautogui.moveTo(769, 320, duration=0)
        pyautogui.click()

        # download document
        pyautogui.moveTo(815, 390, duration=1)
        pyautogui.click()
        time.sleep(0.5)
        pyautogui.click()

        pyautogui.moveTo(958, 671, duration=1)
        pyautogui.click()


        time.sleep(60 * 4)

        # move files in download_directory to output_directory
        for root, dirs, files in os.walk(download_dir):
            for f in files:
                # prefix downloaded file with page_link_counter so that they are in order
                shutil.move(os.path.join(root, f), output_dir + '/' + str(result_number).zfill(4) + '_' + f)
    return documents_parsed


def newsbank_scrape(url, download_dir, output_dir):
    try:
        ################################################################################################################
        # Set up webdriver
        print("Starting WebScraper 🌐➡📚")

        #time.sleep(60 * 60 * 2.6)  # sleep 2.6 hours
        #time.sleep(60 * 60 * 1.6)  # sleep 2.6 hours

        webdriver_options = Options()
        # webdriver_options.add_argument('--headless')
        webdriver_options.add_argument('--no-sandbox')
        webdriver_options.add_argument('--disable-dev-shm-usage')
       # folder_path_to_store_session = "C:\\Users\\mrt64\\AppData\\Local\\Google\\Chrome\\User Data"
       # webdriver_options.add_argument("user-data-dir=" + folder_path_to_store_session)

        s = Service(ChromeDriverManager().install())   # laptop
        # s = Service('chromedriver/chromedriver')   # desktop
        driver = webdriver.Chrome(service=s, options=webdriver_options)

        driver.maximize_window()
        # driver.set_window_size(1400, 1000)

        driver.get(url)
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")  # Scroll to the bottom of the page

        time.sleep(6)  # Wait for all the images to load

        data = driver.execute_script("return document.documentElement.outerHTML")
        good_soup = BeautifulSoup(data, "lxml")
        #
        ################################################################################################################

        ################################################################################################################
        # Check if we need to log in - find id=btnLoginReg
        login_container = good_soup.find_all(id="btnLoginReg")  # good_soup.find_all('id', {'id': 'username'})
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
            time.sleep(10)
        #
        ################################################################################################################

        ################################################################################################################
        # Traverse the pages needed to be downloaded

        # open the last page we visited and continue
        if os.path.exists(output_dir + '/visited_urls.txt'):
            with open(output_dir + '/visited_urls.txt', 'r') as f:
                lines = f.readlines()
                last_line = lines[-1]
                driver.get(last_line)
                time.sleep(6)

        data = driver.execute_script("return document.documentElement.outerHTML")
        good_soup = BeautifulSoup(data, "lxml")

        # <div class="search-hits__meta--total_hits">
        #       378 Results
        #     </div>
        expected_download_count = 2913 # int(driver.find_element(By.CLASS_NAME, "search-hits__meta--total_hits").text.replace(',', '').replace('Results', '').replace(' ', ''))

        download_count = 0
        download_count += download_this_page(download_dir, output_dir, driver, good_soup)

        # find a tag with title = "Go to next page"


        #is_there_a_next_page = driver.find_element(By.CSS_SELECTOR, 'a[title="Go to next page"]')
        chunks_download = 1

        while download_count < expected_download_count:
            # click next page
            #  < a title = "Go to next page" href = "/apps/readex/results?page=1&amp;p=HN-SARDM&amp;t=year%3A1955%211955&amp;f=advanced&amp;sort=YMD_date%3AA&amp;val-base-0=white&amp;fld-base-0=alltext&amp;bln-base-1=and&amp;val-base-1=toothpaste&amp;fld-base-1=alltext&amp;bln-base-2=and&amp;val-base-2=bantu&amp;fld-base-2=alltext&amp;bln-base-3=and&amp;val-base-3=coloured&amp;fld-base-3=alltext" > next › < / a >
            #driver.find_element(By.CSS_SELECTOR, 'a[text="Next"]').click()
            driver.find_element(By.LINK_TEXT, 'Next').click()
            time.sleep(6)
            data = driver.execute_script("return document.documentElement.outerHTML")
            good_soup = BeautifulSoup(data, "lxml")

            # append the href url to a file
            current_page_being_parsed = driver.current_url
            with open(output_dir + '/visited_urls.txt', 'a') as f:
                f.write(current_page_being_parsed + '\n')

            time.sleep(10)

            download_count += download_this_page(download_dir, output_dir, driver, good_soup)
            chunks_download += 2

            # fix for download rate limit
            if(chunks_download > 300) and download_count > -1:
                #time.sleep(60*60*2.1) # sleep 2.1 hours

                driver.get(current_page_being_parsed)
                data = driver.execute_script("return document.documentElement.outerHTML")
                good_soup = BeautifulSoup(data, "lxml")

                ################################################################################################################
                # Check if we need to log in - find id=btnLoginReg
                login_container = good_soup.find_all(id="btnLoginReg")  # good_soup.find_all('id', {'id': 'username'})
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
                    time.sleep(10)
                #
                ################################################################################################################

                chunks_download = 0

            # check if there is a next page
            driver.get(current_page_being_parsed)
            time.sleep(6)

            #is_there_a_next_page = driver.find_element(By.CSS_SELECTOR, 'a[title="Go to next page"]')
        #
        ################################################################################################################

        if expected_download_count != download_count:
            print(f" WARNING! Downloaded count does not match expected count.  Expected: {expected_download_count}  Downloaded: {download_count}")

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

# Rand Daily Mail
#scrape_this_url = "https://eresources.remote.bl.uk:2159/apps/readex/results?p=HN-SARDM&sort=YMD_date%3AA&fld-nav-0=YMD_date&val-nav-0=1940%20-%201999&f=advanced&val-base-0=white&fld-base-0=alltext&bln-base-1=and&val-base-1=native&fld-base-1=alltext&bln-base-2=and&val-base-2=bantu&fld-base-2=alltext&bln-base-3=and&val-base-3=coloured&fld-base-3=alltext"

# Sunday Times
scrape_this_url = "https://eresources.remote.bl.uk:2159/apps/news/results?sort=YMD_date%3AD&p=WORLDNEWS&t=pubname%3A16ED7D43CFB7D6F4%21Sunday%2BTimes&maxresults=20&f=advanced&val-base-0=white&fld-base-0=alltext&bln-base-1=and&val-base-1=native&fld-base-1=alltext&bln-base-2=and&val-base-2=coloured&fld-base-2=alltext&bln-base-3=and&val-base-3=bantu&fld-base-3=alltext&fld-nav-1=YMD_date&val-nav-1=1940%20-%201999"

# test url
# scrape_this_url = "https://eresources.remote.bl.uk:2159/apps/readex/results?p=HN-SARDM&t=year%3A1955%211955&f=advanced&sort=YMD_date%3AA&val-base-0=white&fld-base-0=alltext&bln-base-1=and&val-base-1=toothpaste&fld-base-1=alltext&bln-base-2=and&val-base-2=bantu&fld-base-2=alltext&bln-base-3=and&val-base-3=coloured&fld-base-3=alltext"

#
scrape_this_url = "https://eresources.remote.bl.uk:2159/apps/news/results?p=WORLDNEWS&t=pubname%3A114CF48AE24B9638%7C142051F45F422A02%7C13D5DA85AE05A305%7CLTIB%7C138FFE8785E79426%7CFIN2%7C1386BF60B4F67060%7CTRSB%7CPHIB%7CSMH2%21Multiple%2520Sources%2520%2810%29&sort=YMD_date%3AA&maxresults=20&f=advanced&val-base-0=apartheid&fld-base-0=alltext&bln-base-1=and&val-base-1=native&fld-base-1=alltext&fld-nav-0=YMD_date&val-nav-0=1940%20-%201999"

print("starting to scrape...")

# delete all files in download_directory
for root, dirs, files in os.walk(download_directory):
    for f in files:
        os.unlink(os.path.join(root, f))

print(f"  URL: {scrape_this_url}")

newsbank_scrape(scrape_this_url, download_directory, output_directory)

print("Scraping complete.")
#    restartScrape = inp("Keep scraping? ('y' for yes or 'n' for no) ")
#    if restartScrape == "n":
#        print("Scraping ended.")
#        break
