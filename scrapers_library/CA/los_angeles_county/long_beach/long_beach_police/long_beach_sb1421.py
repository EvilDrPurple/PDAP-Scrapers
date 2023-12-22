import os
import time

import requests
from requests_html import HTMLSession
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.action_chains import ScrollOrigin
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from content import videos


def test():
    url = "https://citydocs.longbeach.gov/LBPDPublicDocs/Browse.aspx?id=198677&dbid=0&repo=LBPD-PUBDOCS"

    chrome_options = Options()
    #chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    gather_links(driver)

    input()
    driver.quit()


def gather_links(driver, recursive_call=False):
    wait = lambda: WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "EntryNameColumn"))
    )

    wait()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    row_list = soup.find_all(class_="EntryNameColumn")

    p = 0
    while p < len(row_list) and "FolderIcon" in str(row_list[p]):
        link_text = row_list[p].get_text().strip()
        folder_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, link_text)))
        folder_link.click()

        links = gather_links(driver, recursive_call=True)

        driver.back()
        wait()
        p = p + 1

    table = driver.find_element(By.CLASS_NAME, "browseMain")
    scroll_origin = ScrollOrigin.from_element(table)
    row_lists = [row_list]
    row_list = None

    while row_lists[-1] != row_list:
        if row_list:
            row_lists.append(row_list)

        ActionChains(driver)\
            .scroll_from_origin(scroll_origin, 0, 1500)\
            .perform()
        
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        row_list = soup.find_all(class_="EntryNameColumn")

    row_list = [row for row_list in row_lists for row in row_list]
    row_list = set(row_list)
    for row in row_list:
        print(row.get_text().strip())
    print(f"\n{len(row_list)}")
    
    return row_list


def download_video_group(group_name, homepage_id, group_filename, start, end):
    savedir = f"./data/{group_name}/"
    homepage_url = f"https://citydocs.longbeach.gov/LBPDPublicDocs/Browse.aspx?id={homepage_id}&dbid=0&repo=LBPD-PUBDOCS"
    session = requests.Session()
    r = session.get(homepage_url)
    cookies = r.cookies

    for id in range(start, end):
        video_url = f"https://citydocs.longbeach.gov/LBPDPublicDocs/mediahandler.ashx?id={id}&t=638384321518479423&dbid=0&repo=LBPD-PUBDOCS"
        filename = f"{group_filename}-{id - start + 1}.mp4"
        download_file(video_url, savedir, filename, session=session, cookies=cookies)

    session.close()


def download_file(url, savedir, filename=None, disable=False, session=None, cookies=None):
    """Downloads a file to a given directory.

    Args:
        url (str): Url of the file to download.
        savedir (str): Directory where the file will be saved.
        filename (str, optional): Name the file will be saved as. Defaults to last part of url.
        disable (bool, optional): Whether or not to disable the progress bar in the command line. Defaults to False.
    """
    if filename is None:
        filename = url.split("/")[-1]

    if os.path.exists(savedir + filename):
        if not disable:
            print("File already exists: " + filename)
        return

    os.makedirs(savedir, exist_ok=True)

    if session:
        r = session.get(url, cookies=cookies, stream=True)
        print(r.content)
    else:
        r = requests.get(url, stream=True)

    total = int(r.headers.get("content-length", 0))
    progress_bar = tqdm(total=total, unit="iB", unit_scale=True, desc=filename, disable=disable)

    with open(savedir + filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            progress_bar.update(len(chunk))
            f.write(chunk)

    progress_bar.close()


def main():
    test()
    return
    for video in videos:
        download_video_group(video["name"], video["id"], video["filename"], video["start"], video["end"])


if __name__ == "__main__":
    main()