import json
import re
from bs4 import BeautifulSoup
import requests
import os

def strip(html):
    h = re.sub(r'<','\n<',html)
    return BeautifulSoup(h,features="html.parser").get_text()   


def search(text:str, skip=0, limit=50, field="lemmatized_text", timeout='5s')->object:
    username = 'admin'
    password = os.getenv('RGPASS')
    print('password=',password)
    elastic_endpoint = 'http://13.79.79.34:9094/elasticsearch/'
    q = {
        "from": skip,
        "size": limit,
        "timeout": timeout,
        # "track_total_hits": 100,
        "_source": [ "obj_id", "date_modified","title","announce","uannounce", "link_title", "url" ],
        "query": {
            "match": {
            f"{field}": {
                "query": text
                }
            }
        }    
    }
    
    rjson = {}
    r = requests.post(f'{elastic_endpoint}articles/_search', 
        headers = {'Content-Type': 'application/json; charset=UTF-8'}, 
        auth=(username,password),
        data= json.dumps(q))
#                       data=query_str.encode('utf-8'))
    try:
        rjson=r.json()
    except:
        pass

    return rjson

