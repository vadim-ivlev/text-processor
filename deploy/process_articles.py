
import psycopg2
import time

import text_processor
import simplejson as json

DSN = "host= port=5432 dbname=rgdb user=root password=******2011"

def execute(DSN,sql, *args):
    records = None
    err = None    
    start = time.time()

    try:
        con = psycopg2.connect( DSN )

        cur = con.cursor()
        cur.execute(sql, *args)
        rows = cur.fetchall()
        cols = [x[0] for x in cur.description]

        # with con:
        #     with con.cursor() as cur:
        #         cur.execute(sql, *args)
        #         rows = cur.fetchall()
        #         cols = [x[0] for x in cur.description]

        records = [dict(zip(cols,row)) for row in rows]

    except Exception as ex:
        err = str(ex)
        print("execute error!!! ",err)
    else:
        print("execute success!!!")
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
    print("Executing get_records()")
    res = execute(DSN,f'SELECT * FROM articles LIMIT {num_records}' )
    return res

def process_records(records):
    """
    Adds results of NLP processing to records
    """
    print(f'Executing process_records(records), Record number = {len(records)}')
    for rec in records:
        text_values = [rec['title'], rec['link_title'], rec['announce'], rec['uannounce'], rec['full-text'] ]
        # . в начале чтоб удалить глюк библиотеки
        combined_text = '. '+'. '.join(v for v in text_values if v is not None)
        o = text_processor.process_text(combined_text, clear=True)
        # print(json.dumps(o,indent=2, ensure_ascii=False))
        entities_text = ', '.join(r['name'] for r in o['entities_list'])

        rec['entities_text'] = entities_text
        rec['lemmatized_text'] = o['lemmatized_text']
        rec['entities_grouped'] = o['entities_grouped']
        rec['process_status'] = 'success'

    return records, None, 0

def update_records(records):
    # TODO
    print(f'Executing update_records(records), Record number = {len(records)}')
    print(json.dumps(records,indent=2, ensure_ascii=False))
    return None, "not implemented", 0


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


    new_rec_timeout = 3 #10 * 60

    # бесконечно повторяем одни и те же действия
    for _ in range(10):    

        # извлекаем порцию записей из бд
        new_records, err, duration = repeat_until_success(get_records,1)

        # если в базе данных нет записей для обработки ждем и начинаем сначала
        if new_records is None or len(new_records) == 0:
            print(f'Waiting {new_rec_timeout} sec for new records to appear in database ...')
            time.sleep(new_rec_timeout)
            continue
        
        # обрабатываем порцию записей
        processed_records, err, duration = repeat_until_success(process_records, new_records, wait=3)

        # сохраняем порцию в базу данных 
        saved_records, err, duration = repeat_until_success(update_records, processed_records)



if __name__ == '__main__':
    main()        



