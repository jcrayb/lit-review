from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time
import itertools
import pandas as pd

def scrape(query):
    url = "https://scholar.google.com/"

    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(options=op)
    with driver as browser:
        browser.set_window_size(1024, 768)
        browser.get(url)
        action = ActionChains(driver)

        results_div = driver.find_element(By.CSS_SELECTOR, "input[name='q']")
        action.move_to_element(results_div).click().send_keys(query).perform()
        action.move_to_element(results_div).click().send_keys(Keys.ENTER).perform()

        #q_button = driver.find_element(By.CSS_SELECTOR, "#gs_hdr_tsb")

        time.sleep(2)

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        articles = soup.find_all("div", {"class": 'gs_r'})
    
    return articles