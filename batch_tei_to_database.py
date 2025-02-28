'''
DOCUMENTATION:

argv order  : <journal_id> <pdf_directory> <tei_directory>
description :
    query to database for all articles with <journal_id>,
    checks into <tei_directory> for its extracted tei/xml file,
    determine its status (success/error) and updates article record in database.
    deletes their corresponding pdf file in <pdf_directory>. 

changelog:
    - 27/02/2024: first release
'''

import os
import sys
import json

import MySQLdb

# get inputs
try:
    journal_id, pdf_dir, tei_dir = sys.argv[1:]
    journal_id = int(journal_id)
    if not os.path.exists(pdf_dir) or not os.path.exists(tei_dir): raise Exception()
except:
    print('Error parsing argv. The order is: <journal_id> <pdf_directory> <tei_directory>')
    exit()
__dir__ = os.path.dirname(os.path.abspath(__file__))
tei_dir_files = set(os.listdir(tei_dir))

with open(f'{__dir__}\\config.json', 'r') as f:
    CONFIG = json.loads(f.read())

try:
    conn = MySQLdb.connect(
        host     = CONFIG['db_host'],
        user     = CONFIG['db_user'],
        passwd   = CONFIG['db_pass'],
        database = CONFIG['db_name']
    )
    cursor = conn.cursor()
    print('Connected to database.')
    
    cursor.execute(
        '''SELECT article_id FROM grobid_references 
        WHERE journal_id = %s
        AND pdf_downloaded = 1
        AND pdf_processed = 0''',
        (journal_id, )
    )
    rows = cursor.fetchall()
    for row in rows:
        article_id = row[0]

        if f'{article_id}.grobid.tei.xml' in tei_dir_files: # tei/xml found
            cursor.execute(
                'UPDATE grobid_references SET pdf_processed = 1 WHERE article_id = %s', 
                (article_id, )
            )
        else: 
            output_file = next((f for f in tei_dir_files if f.startswith(str(article_id)) and f.endswith('.txt')), False)

            if output_file: # error pdf to tei/xml
                with open(f'{tei_dir}/{output_file}', 'r') as f:
                    log = f'GROBID Error, filename:{output_file}, content:{f.read()}\n'
                cursor.execute(
                    '''UPDATE grobid_references 
                    SET pdf_processed = -1, log = CONCAT(COALESCE(log, ''), %s) 
                    WHERE article_id = %s''', 
                    (log, article_id)
                )

            else: # other error 
                cursor.execute(
                    'UPDATE grobid_references SET pdf_processed = -2 WHERE article_id = %s', 
                    (article_id, )
                )
        
    conn.commit()

    # if all is OK, delete pdfs
    for article_id, in rows:
        pdf_file = f'{pdf_dir}/{article_id}.pdf'
        if os.path.exists(pdf_file): os.remove(pdf_file)
except:
    conn.rollback()
finally:
    conn.close()
