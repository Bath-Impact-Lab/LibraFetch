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

def askDialog():
    return tkinter.filedialog.askdirectory()


def inp(text):
    return input(text)


ssl._create_default_https_context = ssl._create_unverified_context

output_directory = "C:/Users/mrt64/OneDrive - University of Bath/Student-Meetings-Notes/Alice/scraped_newsbank"
download_directory = "C:/Users/mrt64/Downloads"

def readex_image_scrape(url, download_dir, output_dir):
    try:
        webdriver_options = Options()
        #webdriver_options.add_argument('--headless')
        webdriver_options.add_argument('--no-sandbox')
        webdriver_options.add_argument('--disable-dev-shm-usage')

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

        # Find the List of documents to scrape:
        #
        # <ul class="o-list-bare ui-dv-page-list js-page-list" style="height:1022px">
        # 	<li class="ui-dv-page-list__item" data-page-no="1"><a class="ui-dv-page-list__link js-page-link" data-page-no="1"><span>img 1: Constitution of the ANC (1919)</span><span class="ui-dv-page-list__meta-info u-d-none u-d-inline-block@desktop js-page-link-tippy" data-tippy="" data-original-title="<strong>Contributor</strong>: Senate House Library, University of London  &amp; ICS<br /><strong>Archive Reference</strong>: -">i</span></a></li>
        # 	<li class="ui-dv-page-list__item is-selected" data-page-no="2"><a class="ui-dv-page-list__link js-page-link is-selected" data-page-no="2"><span>img 2:</span><span class="ui-dv-page-list__meta-info u-d-none u-d-inline-block@desktop js-page-link-tippy" data-tippy="" data-original-title="<strong>Contributor</strong>: Senate House Library, University of London  &amp; ICS<br /><strong>Archive Reference</strong>: -">i</span></a></li>
        # 	...
        pyautogui.FAILSAFE = False
        pyautogui.moveTo(10, 10, duration=1)

        # close GDRP popup
        pyautogui.moveTo(1569, 1289, duration=1)
        pyautogui.click()

        # @todo switch to lite viewer to allow filename save
        pyautogui.moveTo(1950, 235, duration=1)
        pyautogui.click()
        time.sleep(4)


        docs_container = good_soup.find_all('ul', {'class': 'ui-dv-page-list'})
        page_link_counter = 1
        for documents_to_click_and_download in docs_container[0].find_all('li', {'class': 'ui-dv-page-list__item'}):
            #@todo continue here
            document_name = documents_to_click_and_download.text

            # remove the "i" from the end of the document name
            #pattern = r"^'|'i$"
            #formatted_document_name = re.sub(pattern, '', document_name)
            #time.sleep(1)
            # click this link
            link = driver.find_element(By.CSS_SELECTOR, 'li.ui-dv-page-list__item[data-page-no="' + str(page_link_counter) + '"]')
            link.click()

            # sleep for random time between 3 and 9 seconds
            time.sleep(0.5) # time.sleep(random.randint(1, 2))

            # check document doesn't already exist


            #   click download button
            #<button id="download" class="toolbarButton download hiddenMediumView" title="Download" tabindex="34" data-l10n-id="download" >
            #    <span data-l10n-id="download_label">Download </span>
            #</button>


            #<div class="ui-dv-pdf-container js-pdf-container" style="height:1187px">
            #            <iframe width="100%" height="100%" frameborder="0" title="Document viewer" src="/boa/pdfjs/viewer.html" data-lf-form-tracking-inspected-dzlr5a50aqy4boq2="true" data-lf-yt-playback-inspected-dzlr5a50aqy4boq2="true" data-lf-vimeo-playback-inspected-dzlr5a50aqy4boq2="true"></iframe><iframe width="100%" height="100%" frameborder="0" title="Document viewer" src="/boa/pdfjs/viewer.html" data-lf-form-tracking-inspected-dzlr5a50aqy4boq2="true" data-lf-yt-playback-inspected-dzlr5a50aqy4boq2="true" data-lf-vimeo-playback-inspected-dzlr5a50aqy4boq2="true"></iframe></div>

            # move to download button in lite browser
            pyautogui.moveTo(1915, 313, duration=0.5)
            pyautogui.click()

            #time.sleep(1)

            # @todo confirm location
            pyautogui.moveTo(966, 866, duration=1.5)
            pyautogui.click()

            time.sleep(3)

            # move files in download_directory to output_directory
            for root, dirs, files in os.walk(download_dir):
                for f in files:
                    # prefix downloaded file with page_link_counter so that they are in order
                    shutil.move(os.path.join(root, f), output_dir + '/' + str(page_link_counter) + '_' + f)

            #time.sleep(5)

            #' switch to

            #pyautogui.moveTo(2445, 175, duration=1)

#            pdf_element = driver.find_element(By.CLASS_NAME, "body")

#            action = ActionChains(driver)


#            action.move_to_element_with_offset(pdf_element, xoffset, yoffset).click().build().pperform()

            #action.click_and_hold().perform()
            #action

            #download_link = driver.find_element(By.CLASS_NAME, "download")
            ##download_link.click()

            #document_url = documents_to_click_and_download['href']

            page_link_counter += 1

        # click each document in list

        # download a document:
        #   <button id="download" class="toolbarButton download hiddenMediumView" title="Download" tabindex="34" data-l10n-id="download">
        #       <span data-l10n-id="download_label">Download</span>
        #   </button>
        #for j in range(0, len(documents_to_scrape) - 1):
#            img_src = img_container[j].get("src")
 #           name = img_src.rsplit("/", 1)[-1]
  #          try:
   #             urlretrieve(img_src, os.path.join(scrape_directory, os.path.basename(img_src)))
    #            print("Scraped " + name)
     #       except Exception as e:
      #          print(e)
        time.sleep(3)
        driver.close()
        return page_link_counter
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
