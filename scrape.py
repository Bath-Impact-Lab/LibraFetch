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


def shutterstock_videoscrape():
    try:
        # chromepath = ChromeDriverManager().install()
        # print("ChromeDriverManager path=" + chromepath)

        # service = Service(ChromeDriverManager().install()) #This installs or finds the new version of chrome driver if not available and links to path automatically.
        webdriver_options = Options()
        webdriver_options.add_argument('--headless')
        webdriver_options.add_argument('--no-sandbox')
        webdriver_options.add_argument('--disable-dev-shm-usage')
        # driver = webdriver.Chrome(service=service, options=options)

        # driver = webdriver.Chrome(options=webdriver_options)
        # driver = webdriver.Chrome(ChromeDriverManager().install()) #This installs or finds the new version of chrome driver if not available and links to path automatically.

        s = Service('chromedriver/chromedriver')
        driver = webdriver.Chrome(service=s, options=webdriver_options)

        driver.maximize_window()
        for i in range(1, searchPage + 1):
            url = "https://www.shutterstock.com/video/search/" + searchTerm + "?page=" + str(i)
            driver.get(url)
            print("Page " + str(i))
            for j in range(0, 50):
                while True:
                    container = driver.find_elements_by_xpath(
                        "//div[@data-automation='VideoGrid_video_videoClipPreview_" + str(j) + "']")
                    if len(container) != 0:
                        break
                    if len(driver.find_elements_by_xpath(
                            "//div[@data-automation='VideoGrid_video_videoClipPreview_" + str(
                                j + 1) + "']")) == 0 and i == searchPage:
                        driver.close()
                        return
                    time.sleep(10)
                    driver.get(url)
                container[0].click()
                while True:
                    wait = WebDriverWait(driver, 60).until(ec.visibility_of_element_located(
                        (By.XPATH, "//video[@data-automation='VideoPlayer_video_video']")))
                    video_url = driver.current_url
                    data = driver.execute_script("return document.documentElement.outerHTML")
                    scraper = BeautifulSoup(data, "lxml")
                    video_container = scraper.find_all("video", {"data-automation": "VideoPlayer_video_video"})
                    if len(video_container) != 0:
                        break
                    time.sleep(10)
                    driver.get(video_url)
                video_array = video_container[0].find_all("source")
                video_src = video_array[1].get("src")
                name = video_src.rsplit("/", 1)[-1]
                try:
                    urlretrieve(video_src, os.path.join(scrape_directory, os.path.basename(video_src)))
                    print("Scraped " + name)
                except Exception as e:
                    print(e)
                driver.get(url)
    except Exception as e:
        print(e)


def shutterstock_imagescrape():
    try:
        webdriver_options = Options()
        webdriver_options.add_argument('--headless')
        webdriver_options.add_argument('--no-sandbox')
        webdriver_options.add_argument('--disable-dev-shm-usage')
        # driver = webdriver.Chrome(ChromeDriverManager().install(), options=webdriver_options) #chrome_options is deprecated

        s = Service('chromedriver/chromedriver')
        driver = webdriver.Chrome(service=s, options=webdriver_options)

        driver.maximize_window()
        for i in range(1, searchPage + 1):
            url = "https://www.shutterstock.com/search?searchterm=" + searchTerm + "&sort=popular&image_type=" + image_type + "&search_source=base_landing_page&language=en&page=" + str(
                i)
            driver.get(url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")  # Scroll to the bottom of the page
            time.sleep(4)  # Wait 4 seconds for all the images to load
            data = driver.execute_script("return document.documentElement.outerHTML")
            print("Page " + str(i))
            scraper = BeautifulSoup(data, "lxml")
            img_container = scraper.find_all("img", {"class": "z_h_9d80b z_h_2f2f0"})
            for j in range(0, len(img_container) - 1):
                img_src = img_container[j].get("src")
                name = img_src.rsplit("/", 1)[-1]
                try:
                    urlretrieve(img_src, os.path.join(scrape_directory, os.path.basename(img_src)))
                    print("Scraped " + name)
                except Exception as e:
                    print(e)
        driver.close()
    except Exception as e:
        print(e)


def boa_image_scrape(url):
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

        driver.close()
        return page_link_counter
    except Exception as e:
        print(e)


print("Scrape")

#  Top:
#  https://microform.digital/boa/collections/84/apartheid-through-the-eyes-of-south-african-political-parties-1948-1994
#
#   Containing 7,499 pages belonging to 33 documents housed in 4 volumes.
#
#   Documents:
#     https://microform.digital/boa/collections/84/apartheid-through-the-eyes-of-south-african-political-parties-1948-1994/volumes
#
#     Contains 4 volumes:
#
#     https://microform.digital/boa/documents/11165/papers-relating-to-the-anc-1919-1994
#       6 results
volume1 = {
    'publications-of-umkonto-we-sizwe-1961-1982': "https://microform.digital/boa/documents/11167/publications-of-umkonto-we-sizwe-1961-1982",
    'press-releases-of-the-south-african-coloured-peoples-congress-1965-1967': "https://microform.digital/boa/documents/11168/press-releases-of-the-south-african-coloured-peoples-congress-1965-1967",
    'publications-of-congress-of-the-people-1955': "https://microform.digital/boa/documents/11169/publications-of-congress-of-the-people-1955",
    'papers-of-the-vigilance-association-1944-1946': "https://microform.digital/boa/documents/11170/papers-of-the-vigilance-association-1944-1946",
    'papers-relating-to-the-anc-1919-1994': "https://microform.digital/boa/documents/11165/papers-relating-to-the-anc-1919-1994",
    'publications-of-the-anc-youth-league-1945-1957': "https://microform.digital/boa/documents/11166/publications-of-the-anc-youth-league-1945-1957",
}
#
#     https://microform.digital/boa/collections/84/volumes/619/papers-from-the-national-party-and-other-pro-apartheid-parties-1944-1986
#       8 results
volume2 = {
    'papers-of-the-national-party-1948-1986': "https://microform.digital/boa/documents/11171/papers-of-the-national-party-1948-1986",
    'papers-of-the-conservative-party-1982-1985': "https://microform.digital/boa/documents/11172/papers-of-the-conservative-party-1982-1985",
    'papers-of-the-national-conservative-party-1980-1981': "https://microform.digital/boa/documents/11173/papers-of-the-national-conservative-party-1980-1981",
    'papers-of-the-south-african-labour-party-1946-1954': "https://microform.digital/boa/documents/11174/papers-of-the-south-african-labour-party-1946-1954",
    'papers-of-the-new-republic-party-1976-1981': "https://microform.digital/boa/documents/11175/papers-of-the-new-republic-party-1976-1981",
    'papers-of-the-herstigte-nasionale-party-van-suid-afrika-1969-1985': "https://microform.digital/boa/documents/11176/papers-of-the-herstigte-nasionale-party-van-suid-afrika-1969-1985",
    'papers-of-the-united-party-1948-1986': "https://microform.digital/boa/documents/11177/papers-of-the-united-party-1948-1986",
    'papers-of-the-african-democratic-party-1944': "https://microform.digital/boa/documents/11178/papers-of-the-african-democratic-party-1944",
}
#
#     https://microform.digital/boa/collections/84/volumes/620/papers-from-anti-apartheid-parties-1934-1987
#       16 Results
volume3 = {
    'papers-of-the-labour-party-of-south-africa-1972-1981': "https://microform.digital/boa/documents/11179/papers-of-the-labour-party-of-south-africa-1972-1981",
    'papers-of-the-pan-africanist-congress-of-azania-1959-1986': "https://microform.digital/boa/documents/11180/papers-of-the-pan-africanist-congress-of-azania-1959-1986",
    'papers-of-the-progressive-party-and-the-progressive-federal-party-1959-1987': "https://microform.digital/boa/documents/11181/papers-of-the-progressive-party-and-the-progressive-federal-party-1959-1987",
    'papers-of-the-african-democratic-party-and-the-democratic-party-1944-1974': "https://microform.digital/boa/documents/11182/papers-of-the-african-democratic-party-and-the-democratic-party-1944-1974",
    'papers-of-the-liberal-party-of-south-africa-1946-1968': "https://microform.digital/boa/documents/11183/papers-of-the-liberal-party-of-south-africa-1946-1968",

    'papers-of-the-south-african-congress-of-democrats-1954-1962': "https://microform.digital/boa/documents/11184/papers-of-the-south-african-congress-of-democrats-1954-1962",
    'papers-of-the-defenders-of-the-constitution-1953-1955': "https://microform.digital/boa/documents/11185/papers-of-the-defenders-of-the-constitution-1953-1955",
    'papers-of-the-revolutionary-party-1934': "https://microform.digital/boa/documents/11186/papers-of-the-revolutionary-party-1934",
    'miscellaneous-anti-apartheid-papers-1957-1977': "https://microform.digital/boa/documents/11187/miscellaneous-anti-apartheid-papers-1957-1977",
    'papers-of-the-south-african-progressive-reform-party-1975': "https://microform.digital/boa/documents/11188/papers-of-the-south-african-progressive-reform-party-1975",

    'papers-of-the-workers-party-of-south-africa-1938-1940': "https://microform.digital/boa/documents/11189/papers-of-the-workers-party-of-south-africa-1938-1940",
    'papers-of-the-union-federal-party-natal-1953-1956': "https://microform.digital/boa/documents/11190/papers-of-the-union-federal-party-natal-1953-1956",
    'papers-of-the-united-democratic-front-1983': "https://microform.digital/boa/documents/11191/papers-of-the-united-democratic-front-1983",
    'papers-of-the-communist-party-of-south-africa-1936-1986': "https://microform.digital/boa/documents/11192/papers-of-the-communist-party-of-south-africa-1936-1986",
    'papers-of-the-unity-movment-of-south-africa-1948-1972': "https://microform.digital/boa/documents/11193/papers-of-the-unity-movment-of-south-africa-1948-1972",

    'papers-of-the-unification-movement-1961-1962': "https://microform.digital/boa/documents/11194/papers-of-the-unification-movement-1961-1962",
}
#
#     https://microform.digital/boa/collections/84/volumes/621/papers-from-independent-candidates-1970-1987
#       3 results
volume4 = {
    'ben-dekker-1970': "https://microform.digital/boa/documents/11195/ben-dekker-1970",
    'louis-kreiner-nd': "https://microform.digital/boa/documents/11196/louis-kreiner-nd",
    'denis-worral-1987': "https://microform.digital/boa/documents/11197/denis-worral-1987",
}

volumes = {
    'papers-relating-to-the-anc-1919-1994': volume1,
    'papers-from-the-national-party-and-other-pro-apartheid-parties-1944-1986': volume2,
    'papers-from-anti-apartheid-parties-1934-1987': volume3,
    'papers-from-independent-candidates-1970-1987': volume4,
}



scrape_this_url = "https://microform.digital/boa/documents/11165/papers-relating-to-the-anc-1919-1994"

#while True:
#    while True:
#        scrape_this_url_new = inp(
#            "Please type a url to scrape ( hit return to accept default:" + scrape_this_url + " )" + ": ")
#        if len(scrape_this_url_new) > 4:
#            scrape_this_url = scrape_this_url_new
#        break
        #    while True:
        #        print("Please select a directory to save your scraped files.")

output_directory = "C:/Users/mrt64/OneDrive - University of Bath/Student-Meetings-Notes/Alice/scraped_boa"
download_directory = "C:/Users/mrt64/Downloads"
        # scrape_directory = askDialog()
    #        if scrape_directory == None or scrape_directory == "":
    #            print("You must select a directory to save your scraped files.")
    #            continue
    #        break
    #    if searchMode == "v":
    #       videoscrape()
    #  if searchMode == "i":
    #     imagescrape()


# @todo look through volumes for urls and change directory name to volume name ( create if doesn't exist )

print("starting to scrape...")

# delete all files in output_directory
for root, dirs, files in os.walk(output_directory):
    for f in files:
        os.unlink(os.path.join(root, f))
    #for d in dirs:
    #    shutil.rmtree(os.path.join(root, d))

# Loop through the volumes and their papers
for volume, papers in volumes.items():
    print(f"Volume: {volume}")
    if not os.path.exists(output_directory + '/' + volume):
        os.makedirs(output_directory + '/' + volume)

    # Loop through the papers in the current volume
    for paper, scrape_this_url in papers.items():
        print(f"  Paper: {paper}")
        print(f"  URL: {scrape_this_url}")
        if os.path.exists(output_directory + '/' + volume + '/' + paper):
            # directory already exists
            print(f"  Directory already exists: {output_directory + '/' + volume + '/' + paper}")
            continue # skip to next paper
        else:
            os.makedirs(output_directory + '/' + volume + '/' + paper)

            document_count = boa_image_scrape(scrape_this_url)
            time.sleep(10)  #let all downloads finish
            downloaded_count = len([name for name in os.listdir(download_directory) if os.path.isfile(name)])

            print(f"  Downloaded: {downloaded_count}")
            print(f"  Expected: {document_count}")

            if downloaded_count != document_count:
                print(f" WARNING! Downloaded count does not match expected count.  Expected: {document_count}  Downloaded: {downloaded_count}")

            # move files in download_directory to output_directory
            for root, dirs, files in os.walk(download_directory):
                for f in files:
                    shutil.move(os.path.join(root, f), output_directory + '/' + volume + '/' + paper + '/' + f)

    print()  # Add a newline for better readability

boa_image_scrape(scrape_this_url)


print("Scraping complete.")
#    restartScrape = inp("Keep scraping? ('y' for yes or 'n' for no) ")
#    if restartScrape == "n":
#        print("Scraping ended.")
#        break


'''    while True:
        searchMode = inp("Search mode ('v' for video or 'i' for image): ")
        if searchMode != "v" and searchMode != "i":
            print("You must select 'v' for video or 'i' for image.")
            continue
        break
    if searchMode == 'i':
        while True:
            image_type = inp("Select image type ('a' for all or 'p' for photo): ")
            if image_type != "a" and image_type != "p":
                print("You must select 'a' for all or 'p' for photo.")
                continue
            break
        if image_type == 'p':
            image_type = 'photo'
        else:
            image_type = 'all'
    while True:
        searchCount = int(inp("Number of search terms: "))
        if searchCount < 1:
            print("You must have at least one search term.")
            continue
        elif searchCount == 1:
            searchTerm = inp("Search term: ")
        else:
            searchTerm = inp("Search term 1: ")
            for i in range(1, searchCount):
                searchTermPart = inp("Search term " + str(i + 1) + ": ")
                if searchMode == "v":
                    searchTerm += "-" + searchTermPart
                if searchMode == "i":
                    searchTerm += "+" + searchTermPart
        break
    while True:
        searchPage = int(input("Number of pages to scrape: "))
        if searchPage < 1:
            print("You must have scrape at least one page.")
            continue
        break
'''
