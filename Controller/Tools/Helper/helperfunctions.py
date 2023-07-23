import json
from pathlib import Path
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def object_visible(element:object):
    # element = body.find_element(locator,locator_name)

    if element.is_displayed() is True :return True
    else: return False
    

def update_json(new_data: dict, filepath: str, data_name: str):
    with open(filepath,'r+') as file:
        file_data = json.load(file)
        file_data[data_name].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent = 4)


def blob_cleanser(text:str):
    text_encode = text.encode('ascii',errors='ignore')
    text_decode = text_encode.decode('utf-8',errors='ignore')
    clean_text = re.sub(r'\n', ' ', text_decode)
    clean_text = re.sub(r'\[(\s[?]\s)\]', '', clean_text)
    clean_text = re.sub(r'\s{2,}', ' ', clean_text)
    return clean_text


def removeDuplicatesFromText(text):
    regex = r'\b(\w+)(?:\W+\1\b)+' 
    return re.sub(regex, r'\1', text, flags=re.IGNORECASE)


def extract_blob(text: str,  post_id:str, filepath: str, data_name: str) -> None:
    """ Blob text from post as text, filename: file.json, dataname:
        json.class. Doest return back any value. This is for
        the NLP machine.
    """ 
    # body_text = blob.find_element(By.ID,'postingbody').text
    clean_text = blob_cleanser(text)
    body_dict = {"id":post_id, "text": clean_text}
    update_json(body_dict,filepath,data_name)
    
def class_by_score(city_score:int, display_city: type) -> None:
    """ Will return a k,v pair based on which scored the highest."""
      # logger.warning(f'NO_CITY_json_data: {json_data},     NO_CITY_json_address:{json_address}')
    if city_score < 1: pass
    elif city_score > 5 and city_score <= 10:
        display_city = type.title()
    elif city_score > 3 and city_score <= 5:
        display_city = type.title()
    elif city_score > 2 and city_score <= 3:
        display_city = type.title()
    elif city_score > 0 and city_score <= 1:
        display_city = type .title()
        return display_city