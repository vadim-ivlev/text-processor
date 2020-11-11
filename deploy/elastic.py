import json
import re
from bs4 import BeautifulSoup
import requests
import os
import inspect
# from pprint import pprint

def strip(html):
    h = re.sub(r'<','\n<',html)
    return BeautifulSoup(h,features="html.parser").get_text()   


def search(text:str, skip=0, limit=20, field="lemmatized_text", timeout='5s', from_date='2000-01-01', to_date='2030-01-01')->object:

    if from_date == '':
        from_date = '2000-01-01'
    if to_date == '':
        to_date = '2030-01-01'

    loc = locals()
    for arg in inspect.getfullargspec(search).args: print(f'{arg:20}:', loc[arg])
    # pprint([(f'{arg:20}:', loc[arg]) for arg in inspect.getfullargspec(search).args ])

    username = 'admin'
    password = os.getenv('RGPASS')
    elastic_endpoint = os.getenv('ELASTIC_ENDPOINT')

# _sql/translate
# {
#   "query": """
#   SELECT SCORE() AS SCORE,obj_id,date_modified   
#   FROM articles WHERE 
#   MATCH(lemmatized_text, 'пингвин') 
#   AND date_modified.keyword >= '2011-03-03' 
#   AND date_modified.keyword <= '2012-03-03' 
#   ORDER BY SCORE DESC
#   LIMIT 10"""
# }

    # q = {
    #     "from": skip,
    #     "size": limit,
    #     "timeout": timeout,
    #     # "track_total_hits": 100,
    #     "_source": [ "obj_id", "date_modified","title","announce","uannounce", "link_title", "url" ],
    #     "query": {
    #         "match": {
    #         f"{field}": {
    #             "query": text
    #             }
    #         }
    #     }    
    # }

    q = {
        "from": skip,
        "size": limit,
        "timeout": timeout,
        "query" : {
            "bool" : {
            "must" : [
                {
                "match" : {
                    "lemmatized_text" : {
                    "query" : text,
                    "operator" : "OR",
                    "prefix_length" : 0,
                    "max_expansions" : 50,
                    "fuzzy_transpositions" : True,
                    "lenient" : False,
                    "zero_terms_query" : "NONE",
                    "auto_generate_synonyms_phrase_query" : True,
                    "boost" : 1.0
                    }
                }
                },
                {
                "range" : {
                    # "date_modified.keyword" : {
                    "date_modified" : {
                    "format": "yyyy-MM-dd",    
                    "from" : from_date,
                    "to" : to_date,
                    "include_lower" : True,
                    "include_upper" : True,
                    "time_zone" : "Z",
                    "boost" : 1.0
                    }
                }
                }
            ],
            "adjust_pure_negative" : True,
            "boost" : 1.0
            }
        },
        "_source" : {
            "includes" : [ "obj_id", "date_modified","title","announce","uannounce", "link_title", "url" ], 
            "excludes" : [ ]
        },
        "sort" : [
            {
            "_score" : {
                "order" : "desc"
            }
            }
        ],
        "track_scores" : True
    }



    rjson = {}
    r = requests.post(f'{elastic_endpoint}articles/_search', 
        headers = {'Content-Type': 'application/json; charset=UTF-8'}, 
        auth=(username,password),
        data= json.dumps(q))
#                       data=query_str.encode('utf-8'))
    try:
        rjson=r.json()
    except Exception as ex:
        print(ex)

    return rjson

