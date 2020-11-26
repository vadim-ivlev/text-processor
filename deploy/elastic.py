import json
import re
from bs4 import BeautifulSoup
import requests
import os
import inspect

def strip(html):
    """"Очищает текст от разметки"""    
    h = re.sub(r'<','\n<',html)
    return BeautifulSoup(h,features="html.parser").get_text()   


def search(text:str, skip=0, limit=20, field="lemmatized_text", timeout='5s', from_date='2000-01-01', to_date='2030-01-01', index='articles')->object:
    """Ищет текст.
    Параметры:
        text - Текст для поиска
        field = 'lemmatized_text' - Название поля по которому искать
        skip = 0 - Сколько Документов пропустить перед выдачей
        limit = 20 - Максимальное количество возвращаемых Документов
        timeout = '5s' - Максимальное время поиска
        lemmatize = True - лемматизировать слова запроса перед поиском
        from_date = '2000-01-01' - Минимальная дата искомого документа
        to_date = '2030-01-01'- Максимальная дата искомого документа
        index = 'articles' - Имя индекса в котором искать документы
    """
    if from_date == '':
        from_date = '2000-01-01'
    if to_date == '':
        to_date = '2030-01-01'

    loc = locals()
    # печатаем полученные аргументы
    for arg in inspect.getfullargspec(search).args: print(f'{arg:20}:', loc[arg])

    username = os.getenv('ELASTIC_USER')
    password = os.getenv('RGPASS')
    # Определено в doker-compose
    elastic_endpoint = os.getenv('ELASTIC_ENDPOINT')

    # SQL вариант запроса
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
    r = requests.post(f'{elastic_endpoint}{index}/_search', 
        headers = {'Content-Type': 'application/json; charset=UTF-8'}, 
        auth=(username,password),
        data= json.dumps(q))
#                       data=query_str.encode('utf-8'))
    try:
        rjson=r.json()
    except Exception as ex:
        print(ex)

    return rjson

