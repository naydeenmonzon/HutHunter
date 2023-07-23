import json
import re
from Tools.Helper.helperfunctions import update_json,extract_blob,object_visible,removeDuplicatesFromText
from selenium.webdriver.common.by import By
import logging
import re
from selenium.common import exceptions
import time
import random
from datetime import date, datetime
from Tools.Connection.MySQLcnx import MySQLcnx
from Tools.Connection.Browser import ChromeDriver
from pathlib import PurePath,Path
import os



p = Path(os.getcwd())




formatter = logging.Formatter('%(levelname)s %(asctime)s: %(message)s',datefmt="%Y-%b-%d %H:%M:%S")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
dh = logging.FileHandler("C:/Users/Administrator/Documents/Projects/www/HutHunter/Log/Logexplorer.log")
dh.setLevel(logging.DEBUG)
logger.addHandler(dh)
dh.setFormatter(formatter)


def pet_type(pet_score:int):
    if pet_score < 1: pets = 'no_pets/unknown'
    elif pet_score == 3: pets = 'cats_only'
    elif pet_score == 5 : pets = 'dogs_only'
    elif pet_score == 8 : pets = 'cats_and_dogs'
    return pets

def jsonaddress(post_id, json_data):      
    json_dict = {"id":post_id}
    json_dict.update(json_data['address'])
    update_json(json_dict,"C:/Users/Administrator/Documents/Projects/www/HutHunter/Data/address.json","address")

def mapbox(driver:object, post_id:str):
    # time.sleep(random.randrange(2))
    default = driver.current_window_handle
    map_box = driver.find_element(By.ID,'map')
    latitude = map_box.get_attribute('data-latitude')
    longitude = map_box.get_attribute('data-longitude')
    json_link = f'https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json'
    driver.switch_to.new_window('tab')
    driver.get(json_link)
    try:
        body_map = driver.find_element(By.TAG_NAME,'pre').text
        json_data = json.loads(body_map)
        jsonaddress(post_id,json_data)
        display_name = json_data['display_name']
        display_address = json_data['address']
    except:
        display_name=''
        display_address=''       
    driver.close()
    driver.switch_to.window(default)
    return {'display_name':display_name,'display_address':display_address}

def filter_shared_line(keywords:list, date_posted:datetime):
    bedroom_count=''
    bathroom_count=''
    sqft_count = ''
    date_available = date_posted
    for key in keywords:
        bedroom = re.search(r'\d+BR',key)
        if bedroom == None: pass
        else: bedroom_count += bedroom.group(0)
        bedroom_count = re.sub('BR','',bedroom_count)
        bathroom = re.search(r'[0-9.]+Ba',key)
        if bathroom == None: pass
        else: bathroom_count += bathroom.group(0)
        bathroom_count = re.sub('Ba','',bathroom_count)
        sqft = re.search(r'[0-9.]+ft2',key)
        if sqft == None: pass
        else: sqft_count += sqft.group(0)
        sqft_count = re.sub('ft2','',sqft_count)
        available = re.search(r'(?<=available )(.)*', key)
        if available == None: pass
        elif available.group(0) == 'now': date_available = date_posted
        else: date_available = datetime.strptime(f'{available.group(0)} {date.today().year}', '%b %d %Y')
    return {'bedroom_count':bedroom_count,'bathroom_count':bathroom_count, 'sqft_count':sqft_count, 'date_available':date_available}

def filter_span_group(keywords:list):
    pet_score = 0
    housing_type=''
    laundry_type=''
    parking_type=''
    other = []
    remove_other = []
    for key in keywords:
        housing = re.search(r'\b(?:apartment|condo|cottage/cabin|duplex|flat|house|in-law|loft|townhouse|manufactured|assisted living|land)\b', key)
        if housing == None: pass
        else: housing_type += housing.group(0)
        remove_other.append(housing_type)
        laundry = re.search(r'\b(?:w/d in unit|w/d hookups|laundry in bldg|laundry on site|no laundry on site)\b', key)
        if laundry == None: pass
        else: laundry_type += laundry.group(0)
        remove_other.append(laundry_type)
        parking = re.search(r'\b(?:carport|attached garage|detached garage|off-street parking|street parking|valet parking|no parking)\b', key)
        if parking == None: pass
        else: parking_type += parking.group(0)
        remove_other.append(parking_type)
        dog = re.search(r'dogs',key)
        if dog == None: pass
        else: pet_score += 5
        remove_other.append('dogs are OK - wooof')
        cat = re.search(r'cats',key)
        if cat == None: pass
        else: pet_score += 3
        remove_other.append('cats are OK - purrr')
        if key in remove_other: pass
        else: other.append(key)
    return {'housing_type':housing_type,'laundry_type':laundry_type,'parking_type':parking_type,'pets_allowed':pet_type(pet_score), 'other':', '.join(other)}

def post_detail(driver: object, links:list):
    default2 = driver.current_window_handle
    driver.switch_to.new_window('tab')
    # extra = driver.current_window_handle
    for link in links:
        driver.get(link)
        # time.sleep(2)
        body = driver.find_element(By.CLASS_NAME,'body')
        body_text = body.find_element(By.ID,'postingbody').text
        
        h1title = body.find_element(By.CLASS_NAME,'postingtitletext')
        try:
            small = h1title.find_element(By.TAG_NAME, 'small').text
            small_city = re.sub(r'[()]', '', small)
            small_city = small_city.split('/')
            small_city = small_city[0].strip()
        except: small_city = ''
        title = h1title.find_element(By.ID,'titletextonly').text
        date_posted = body.find_element(By.CLASS_NAME,'timeago').get_attribute("datetime")[0:10]
        date_posted = datetime.fromisoformat(date_posted)
        dateposted_delta = datetime.now() - date_posted
        days_on_market = dateposted_delta.days
        post_id = body.find_element(By.CSS_SELECTOR,"div[class='postinginfos'] p:nth-child(1)").text
        post_id = re.sub("post id: ","", post_id)
        extract_blob(body_text,post_id,"C:/Users/Administrator/Documents/Projects/www/HutHunter/Data/blob.json","blob")
        try: mapbox_address = driver.find_element(By.CSS_SELECTOR,"div[class='mapaddress']").text
        except exceptions.NoSuchElementException: mapbox_address=''
        try:
            jasonmap = mapbox(driver,post_id)
        except: jasonmap=None
        shared_line = body.find_elements(By.CLASS_NAME,'shared-line-bubble')
        shared_line_list = [line.text for line in shared_line]
        groupA = filter_shared_line(shared_line_list,date_posted)       # bedroom_count, bathroom_count, sqft_count, date_available
        attn_group = body.find_elements(By.CLASS_NAME,'attrgroup')
        attn_group_list = [group.text.split('\n') for group in attn_group[-1:]]
        groupB = filter_span_group(attn_group_list[0])
        address = ''
        if len(mapbox_address) < 1:
            address += mapbox_address + ' ' + small_city + ' California' 
            # + jasonmap['display_address'] + jasonmap['neighbourhood'] + jasonmap['city'] + jasonmap['county'] + jasonmap['state']
            address = removeDuplicatesFromText(address).title()
        elif jasonmap['display_name'] !=None:
            address = jasonmap['display_name']
        else: address=''
        yield {'post_id':post_id,'link':link,'date_posted':date_posted,
               'days_on_market':days_on_market,'amenitiesA':groupA,
               'amenitiesB':groupB,'mapbox_address':mapbox_address,'jasonmap':jasonmap,'title':title,'address':address}
    driver.close()
    driver.switch_to.window(default2)
    
    
def post_links(rows:list, links:list):
    for items in rows:
        info = items.find_element(By.CLASS_NAME,'result-info')
        heading = info.find_element(By.CLASS_NAME,'result-heading')
        link = heading.find_element(By.TAG_NAME,'a').get_attribute("href")
        links.append(link)
    return links

def get_headers(rows:list, _neighborhoods:str, _county:str):
    COMPLETE = 0
    for items in rows:
        info = items.find_element(By.CLASS_NAME,'result-info')
        heading = info.find_element(By.CLASS_NAME,'result-heading')
        link = heading.find_element(By.TAG_NAME,'a').get_attribute("href")
        post_id = items.get_attribute("data-pid")
        repost_id = items.get_attribute("data-repost-of")
        meta = items.find_element(By.CLASS_NAME,'result-meta')
        monthly_rate = meta.find_element(By.CLASS_NAME,'result-price').text
        rate = re.sub(r"[$,]","",monthly_rate)
        date_posted = items.find_element(By.CLASS_NAME,'result-date').get_attribute("datetime")
        hood_name = meta.find_element(By.CLASS_NAME,'result-hood').text
        hood_name_clean = re.sub(r'[()]','', hood_name).strip()
        compile =  re.compile(f'{_neighborhoods}',flags=re.IGNORECASE)
        hood = compile.findall(hood_name_clean)
        if len(hood) > 0:
            hood_match = compile.findall(hood_name_clean)
            hood = hood_match[0]
        else: hood = _county.title()
        yield (post_id, repost_id, link, rate, _county, hood, date_posted)


def amenities(db:str, _table: str, data_list:list, PAGERANGE:int,BAYAREA:str):
    COMPLETE = 0
    for data in data_list:
        post_id = data['post_id']
        housing_type = data['amenitiesB']['housing_type']
        laundry = data['amenitiesB']['laundry_type']
        parking = data['amenitiesB']['parking_type']
        pets = data['amenitiesB']['pets_allowed']
        bedroom = data['amenitiesA']['bedroom_count']
        bath = data['amenitiesA']['bathroom_count']
        sqft =  data['amenitiesA']['sqft_count']
        days_on_market = data['days_on_market']
        date_available = data['amenitiesA']['date_available']
        address = data['address']
        link = data['link']
        other = data['amenitiesB']['other']
        title = data['title']
        _query= (post_id, housing_type, laundry, parking, pets, bedroom, bath, sqft, days_on_market, date_available, address, link, other, title) 
        MySQLcnx.post(db,_table,_query)
        COMPLETE +=1
        COMPLETED = COMPLETE/(PAGERANGE+1)
        logger.debug(f'{BAYAREA.ljust(5)} HEADERS: {round(COMPLETED*100,2)} % LINK: {link}')