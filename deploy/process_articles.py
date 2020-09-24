
import psycopg2
import psycopg2.extras  
import time

import text_processor
import simplejson as json

DSN = "host=134.0.107.93 port=5432 dbname=rgdb user=root password=rosgas2011"

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
    WHERE obj_id IN ( SELECT obj_id FROM articles WHERE process_status IS NULL LIMIT {num_records})
    RETURNING *
    """ 
    res = execute(DSN,sql)
    return res

def process_records(records):
    """
    Adds results of NLP processing to records
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
        rec['entities_grouped'] = o['entities_grouped']
        rec['process_status'] = o['process_status']
        if i%10==0:
            print(f'{i:>15}')
    duration = time.time() - start
    return records, None, duration

def update_records(records):
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
                json.dumps(r['entities_grouped'],indent=2, ensure_ascii=False)
                ) for r in records]

        con = psycopg2.connect( DSN )
        cur = con.cursor()
        psycopg2.extras.execute_values(cur,"""
            UPDATE articles 
            SET  
            process_status = data.process_status,
            lemmatized_text = data.lemmatized_text,
            entities_text = data.entities_text,
            entities_grouped = data.entities_grouped

            FROM (VALUES %s) AS data (obj_id, process_status, lemmatized_text, entities_text, entities_grouped)
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

    # бесконечно повторяем одни и те же действия
    while True:    

        # извлекаем порцию записей из бд
        new_records, err, duration = repeat_until_success(get_records,50)
        print(f'-- Got       {len(new_records)} in {duration:.2f} seconds.')
        
        # если в базе данных нет записей для обработки ждем и начинаем сначала
        if new_records is None or len(new_records) == 0:
            print(f'Waiting {new_rec_timeout} sec for new records to appear in database ...')
            time.sleep(new_rec_timeout)
            continue
        
        # обрабатываем порцию записей
        processed_records, err, duration = repeat_until_success(process_records, new_records, wait=3)
        print(f'-- Processed {len(processed_records)} in {duration:.2f} seconds.    Rate {len(processed_records)/duration:.2f} records/sec.')
        
        # сохраняем порцию в базу данных 
        saved_records, err, duration = repeat_until_success(update_records, processed_records)
        print(f'-- Saved     {len(processed_records)} in {duration:.2f} seconds.')



if __name__ == '__main__':
    main()        



