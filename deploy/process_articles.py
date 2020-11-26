
import psycopg2
import psycopg2.extras  
import time

import text_processor
import simplejson as json
import os
import requests
from pprint import pprint
import datetime
import pytz

# строка подсоединения к Постгресу
DSN = os.getenv('RGDSN')

# эластик
ELASTIC_USER = os.getenv('ELASTIC_USER')
RGPASS = os.getenv('RGPASS')
ELASTIC_ENDPOINT = os.getenv('ELASTIC_ENDPOINT')
ELASTIC_INDEXES = os.getenv('ELASTIC_INDEXES').split('|') if os.getenv('ELASTIC_INDEXES') else []

print(f'RGPASS={RGPASS} DSN={DSN} ELASTIC_ENDPOINT={ELASTIC_ENDPOINT} ELASTIC_INDEXES={ELASTIC_INDEXES}')


def execute(DSN,sql, *args):
    records = None
    err = None    
    start = time.time()

    try:
        con = psycopg2.connect( DSN )

        cur = con.cursor()
        cur.execute(sql, *args)
        con.commit()
        rows = cur.fetchall()
        cols = [x[0] for x in cur.description]
        records = [dict(zip(cols,row)) for row in rows]

    except Exception as ex:
        err = str(ex)
        print("execute error!!! ",err)
    else:
        # print("execute success!!!")
        pass
    finally:
        if "cur" in locals():
            cur.close()
        if "con" in locals():
            con.close()
    return records, err, time.time() - start




def get_records(num_records=30):
    """ 
    Returns specified number of records from article table, 
    setting process_status field value to "processing"
    """
    # print(f"Executing get_records({num_records})")
    sql = f"""
    UPDATE articles 
    SET process_status='processing' 
    WHERE obj_id IN ( SELECT obj_id FROM articles WHERE process_status IS NULL AND migration_status='success' LIMIT {num_records})
    RETURNING *
    """ 
    res = execute(DSN,sql)
    return res

def process_records(records):
    """
    Adds results of NLP to records
    """
    start = time.time()
    # print(f'Executing process_records(records), Record number = {len(records)}')
    for i,rec in enumerate(records):
        text_values = [rec['title'], rec['link_title'], rec['announce'], rec['uannounce'], rec['full-text'] ]
        
        # . в начале чтоб удалить глюк библиотеки
        combined_text = '. '+'. '.join(v for v in text_values if v is not None)
        o = text_processor.process_text(combined_text, clear=True)
        entities_text = ', '.join(r['name'] for r in o['entities_list'])

        rec['lemmatized_text'] = o['lemmatized_text']
        rec['entities_text'] = entities_text
        rec['entities_grouped'] = json.dumps(o['entities_grouped'], ensure_ascii=False)
        rec['process_status'] = o['process_status']
        if i%10==0:
            print(f'{i:>15}')
    duration = time.time() - start
    return records, None, duration

def save_bulk_to_elastic(lines: list, elastic_endpoint:str, index_name:str, username='', password='') -> bool:
    """Формирует текст из линий и сохраняет его в Elastic _bulk API"""

    res = True
    data = '\n'.join(lines)+'\n'
    try:
        r = requests.post(f'{elastic_endpoint}{index_name}/_bulk', 
                            headers = {'Content-Type': 'application/x-ndjson; charset=UTF-8'}, 
                            auth=(username,password),
                            data=data.encode('utf-8'))
        rjson=r.json()
        if rjson.get('errors') is not False:
            pprint(rjson)
            res = False
    except:
        pprint(r)
        res = False
    return res


def save_records_to_elastic(records):
    """
    Сохраняет порцию записей в Эластик
    """
    start = time.time()
    # подготавливаем записи для балка
    lines = []
    for record in records:
        elastic_id = record['obj_id']
        lines.append('{"index" : {"_id" : "'+str(elastic_id)+'"}}')
        record['index_date']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines.append(json.dumps(record, ensure_ascii=False))
    
    saved = [save_bulk_to_elastic(lines, ELASTIC_ENDPOINT, index , ELASTIC_USER, RGPASS ) for index in ELASTIC_INDEXES]
    if all(saved) :
        for record in records:
            record['elastic_status'] = "indexed"
    else:
        print(f'Records were not saved in all idexes: {ELASTIC_INDEXES} {saved}')
    
    duration = time.time() - start
    print(f'-- Indexed in Elastic   {len(records)} in {duration:.2f} seconds.')
    return records





def update_records(records):
    """
    Сохраняет порцию записей в Postgres
    """
    start = time.time()
    err = None
    # print(f'Executing update_records(records), Record number = {len(records)}')
    # print(json.dumps(records,indent=2, ensure_ascii=False))

    try:
        # prepare data
        data = [(r['obj_id'], 
                r['process_status'], 
                r['lemmatized_text'], 
                r['entities_text'], 
                json.dumps(r['entities_grouped'],indent=2, ensure_ascii=False),
                r['elastic_status']
                ) for r in records]

        con = psycopg2.connect( DSN )
        cur = con.cursor()
        psycopg2.extras.execute_values(cur,"""
            UPDATE articles 
            SET  
            process_status = data.process_status,
            lemmatized_text = data.lemmatized_text,
            entities_text = data.entities_text,
            entities_grouped = data.entities_grouped,
            elastic_status = data.elastic_status

            FROM (VALUES %s) AS data (obj_id, process_status, lemmatized_text, entities_text, entities_grouped, elastic_status)
            WHERE articles.obj_id = data.obj_id
            
            """, data)
        con.commit()
        # rows = cur.fetchall()
        # cols = [x[0] for x in cur.description]
        # records = [dict(zip(cols,row)) for row in rows]
        

    except Exception as ex:
        err = str(ex)
        print("Saving error!!! ",err)
    else:
        pass
    finally:
        if "cur" in locals():
            cur.close()
        if "con" in locals():
            con.close()
    return [1], err, time.time() - start


def repeat_until_success(func, *args, wait=60):
    "Повторяет функцию пока она успешно не выполнится"
    while True:
        result, err, duration = func(*args)
        if err is None:
            break
        print(f'Waiting {wait} sec to retry {func.__name__}() ...')
        time.sleep(wait)
    return result, err, duration


def main():
    # res = execute(DSN,'SELECT obj_id,"full-text" FROM articles LIMIT 20' )
    # print(res)


    new_rec_timeout = 1 * 60

    # Выполнять до тепловой смерти вселенной
    while True:    

        # извлекаем порцию записей из бд
        new_records, err, duration = repeat_until_success(get_records,50)
        if len(new_records) > 0:
            print(f'-- Получили {len(new_records)} новых записей за {duration:.2f} секунд.')
        
        # если в базе данных нет записей для обработки ждем и начинаем сначала
        if new_records is None or len(new_records) == 0:
            dt = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
            print(f'Ждем {new_rec_timeout} секунд появления новых статей в базе данных. {dt}')
            time.sleep(new_rec_timeout)
            continue
        
        # обрабатываем порцию записей
        processed_records, err, duration = repeat_until_success(process_records, new_records, wait=3)
        print(f'-- Processed {len(processed_records)} in {duration:.2f} seconds.    Rate {len(processed_records)/duration:.2f} records/sec.')
        
        # сохраняем порцию в эластик 
        processed_records = save_records_to_elastic(processed_records)

        # сохраняем порцию в базу данных 
        saved_records, err, duration = repeat_until_success(update_records, processed_records)
        print(f'-- Saved     {len(processed_records)} in {duration:.2f} seconds.')
        print('---')


if __name__ == '__main__':
    main()        



