'''
DOCUMENTATION:

argv order  : <journal_id> <num_workers> <save_dir> <max_download>
description :
    check if theres any record in grobid_references where journal_id=journal_id,
    if no, copy all record from articles to grobid_references where journal_id=journal_id,
    for each record, download pdf from location_file

changelog:
    - 27/02/2024: first release
'''


import multiprocessing
import requests
import os
import json
import MySQLdb
from sys import argv

__dir__ = os.path.dirname(os.path.abspath(__file__))

with open(f'{__dir__}\\config.json', 'r') as f:
    CONFIG = json.loads(f.read())

def get_conn():
    return MySQLdb.connect(
        host     = CONFIG['db_host'],
        user     = CONFIG['db_user'],
        passwd   = CONFIG['db_pass'],
        database = CONFIG['db_name']
    )

def crawler(nth, num_workers, save_dir, max, queue:multiprocessing.Queue):
    os.makedirs(save_dir, exist_ok=True)

    conn = get_conn()
    cursor = conn.cursor()

    queue.put(f'Crawler-{nth} start, downloading {max} articles...')

    for i in range(1, max+1): 
        cursor.execute(
            f'''SELECT article_id, location_file FROM grobid_references 
            WHERE pdf_downloaded = 0 AND article_id % {num_workers} = {nth} 
            LIMIT 1''')
        row = cursor.fetchone()
        if not row: break

        try:
            id, url = row

            response = requests.get(url)
            response.raise_for_status()
            if 'application/pdf' in response.headers.get('Content-Type', ''):
                with open(f'{save_dir}/{id}.pdf', 'wb') as file:
                    file.write(response.content)
                cursor.execute(f'UPDATE grobid_references SET pdf_downloaded = 1 WHERE article_id = {id}')
                queue.put(f'crawler-{nth}: | count:{i} | Downloaded {id}.pdf')
            else:
                cursor.execute(f'UPDATE grobid_references SET pdf_downloaded = -1 WHERE article_id = {id}')
                queue.put(f'crawler-{nth}: | count:{i} | ERROR: No PDF file found in article_id={id}')
            conn.commit()
        except requests.exceptions.RequestException as e:
            cursor.execute(f'UPDATE articles SET pdf = -1 WHERE article_id = {id}')
            queue.put(f'crawler-{nth}: | count:{i} | ERROR: HTTP request error in article_id={id}')
            conn.commit()
        except Exception as e:
            cursor.execute(f'UPDATE articles SET pdf = -2 WHERE article_id = {id}')
            queue.put(f'crawler-{nth}: | count:{i} | ERROR: Unknown error in article_id={id}')
            conn.rollback() 
    queue.put('__END__')


# ----- batch download articles for journal -----
def main(journal_id, num_workers, save_dir, max):


    print('BEGIN CRAWL')
    print(f'journal_id  = {journal_id}')
    print(f'num_workers = {num_workers}')
    print(f'save_dir    = {save_dir}')
    print(f'max         = {max}')

    # create directory if not exist
    os.makedirs(save_dir, exist_ok=True)

    # check if journal already in grobid_references
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT EXISTS (SELECT 1 FROM grobid_references WHERE journal_id = %s)', (journal_id, ))

        if not cursor.fetchone()[0]:
            print(f'Record with journal_id={journal_id} not found in grobid_references')
            print(f'Copying record from articles where journal_id={journal_id}...')
            cursor.execute(
                '''INSERT INTO grobid_references (article_id, journal_id, location_file)
                SELECT article_id, journal_id, location_file FROM articles
                WHERE journal_id = %s''', (journal_id, ))
            print(f'{cursor.rowcount} rows inserted')
            conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

    queue = multiprocessing.Queue()

    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(target=crawler, args=(i, num_workers, save_dir, max//num_workers, queue))
        p.start()
        processes.append(p)
    
    active_worker = num_workers
    while active_worker > 0:
        msg = queue.get()
        if msg == '__END__':
            active_worker -= 1
        else:
            print(msg)
    
    print('-- all workers ended ---')

    for p in processes:
        p.join()

if __name__ == '__main__':
    # urutan: journal_id, num_workers, save_dir, max_download
    try:
        journal_id, num_workers, save_dir, max_download = argv[1:]
        journal_id   = int(journal_id)
        max_download = int(max_download)
        num_workers  = int(num_workers)
    except:
        print('Error parsing argv. The order is: <journal_id> <num_workers> <save_dir> <max_download>')
        exit()
    main(journal_id, num_workers, save_dir, max_download)