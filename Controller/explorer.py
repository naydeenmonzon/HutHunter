import logging
from webbrowser import Error
from hunters import get_headers, post_links,post_detail,mapbox, amenities
from selenium.webdriver.common.by import By
import time
from Tools.Connection.MySQLcnx import MySQLcnx
from Tools.Connection.Browser import ChromeDriver
from Models.Craigslist import BayArea
import tkinter as tk
from pathlib import PurePath,Path
import os

p = Path(os.getcwd())

formatter = logging.Formatter('%(levelname)s %(asctime)s: %(message)s',datefmt="%Y-%b-%d %H:%M:%S")
Mlogger = logging.getLogger(__name__)
Mlogger.setLevel(logging.INFO)
ih = logging.FileHandler("C:/Users/Administrator/Documents/Projects/www/HutHunter/Log/Logexplorer.log")
ih.setFormatter(formatter)
Mlogger.addHandler(ih)

for sites in BayArea._member_names_:
    with ChromeDriver() as driver:
        driver.get(BayArea[sites]._value_[2])
        original_window = driver.current_window_handle
        BAYAREA = BayArea[sites]._value_[1]
        M_COUNT = int(driver.find_element(By.CLASS_NAME,'totalcount').text) # MASTER COUNT of POST per BAYAREA ex. 3000
        RANGEFROM = int(driver.find_element(By.CLASS_NAME,'rangeFrom').text)   # MASTER COUNT of POST for every PAGE ex. 120        
        RANGETO = int(driver.find_element(By.CLASS_NAME,'rangeTo').text)    # SETS INITIAL RANGE COUNT
        PAGE = 0
        POST_COUNT = 0
        URL = driver.current_url
        Mlogger.info(f'{str(BAYAREA).ljust(5)} COMPLETE: {round(POST_COUNT/M_COUNT)*100} % PAGE: {PAGE} URL: {URL}')
        while RANGETO < M_COUNT:
            RANGEFROM = int(driver.find_element(By.CLASS_NAME,'rangeFrom').text)
            RANGETO = int(driver.find_element(By.CLASS_NAME,'rangeTo').text)      # RANGE COUNT UPDATES EVERY CLICK TO NEXT PAGE
            PAGERANGE = RANGETO-RANGEFROM
            
            rows = driver.find_element(By.CSS_SELECTOR,'#search-results')     
            results = rows.find_elements(By.CLASS_NAME,'result-row')
            
            neighborhood_list=BayArea[sites]._value_[3]
            county=BayArea[sites]._value_[0]
            
            post_queries = get_headers(results,neighborhood_list,county)
            links = post_links(results, links=[])
            MySQLcnx.post_all('craigslist', 'post_heading',post_queries)
                        
            post_data = post_detail(driver,links)
            
            amenities('craigslist','amenities',post_data,PAGERANGE,BAYAREA)

            driver.refresh()
            # time.sleep(2)
            
            if RANGETO >= M_COUNT: break
            RANGETO += 1
            PAGE+=1
            POST_COUNT += len(links)
            URL = driver.current_url
            Mlogger.info(f'{str(BAYAREA).ljust(5)} COMPLETE: {round(POST_COUNT/M_COUNT)*100,2} % PAGE: {PAGE} URL: {URL}')
            
            driver.find_element(By.CSS_SELECTOR,'a[title="next page"]').click()
        
    # except Error: 
    #     Mlogger.error(f'{str(BAYAREA).ljust(5)} COMPLETE: {round(POST_COUNT/M_COUNT)*100,2} % PAGE: {PAGE} URL: {URL} {Error}')  