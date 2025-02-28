import os
import sys
import json
import requests

from flask import Flask, request, send_file
from flask_cors import CORS
import MySQLdb
from grobid_client.grobid_client import GrobidClient

__dir__ = os.path.dirname(os.path.abspath(__file__))

# config
with open('config.json', 'r') as f:
    CONFIG = json.loads(f.read())
with open('grobid.config.json', 'r') as f:
    GROBID_CONFIG = json.loads(f.read())


def get_conn():
    return MySQLdb.connect(
        host     = CONFIG['db_host'],
        user     = CONFIG['db_user'],
        passwd   = CONFIG['db_pass'],
        database = CONFIG['db_name']
    )

def clear_temp():
    temp_directory = f'{__dir__}/_temp/test_article'
    os.makedirs(temp_directory, exist_ok=True)

    for file_name in os.listdir(temp_directory):
        file_path = os.path.join(temp_directory, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)



app = Flask(__name__)
CORS(app)


@app.route("/") # check environment
def check_environment():

    return_data = {
        "info": {
            "cwd": os.getcwd(),
            "python": sys.executable,
        },
        "config" : None,
        "grobid_config" : None,
        "errors" : []
    }

    try:

        if not os.path.isfile(f'{__dir__}/config.json'):
            return_data['errors'].append('ERROR: tidak ditemukan file config.json')
        if not os.path.isfile(f'{__dir__}/grobid.config.json'):
            return_data['errors'].append('ERROR: tidak ditemukan file grobid.config.json')

        return_data['config'] = CONFIG
        return_data['grobid_config'] = GROBID_CONFIG

        # check sql connection and grobid_references table
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'grobid_references';
            """)
            if cursor.fetchone()[0] != 1:
                return_data['errors'].append('ERROR: tidak ditemukan tabel `grobid_references`. import terlebih dahulu tabel dari file grobid_references.sql')
        except:
            return_data['errors'].append('ERROR: error terkoneksi dengan database, pastikan MySQL hidup dan config sudah benar.')
        finally:
            conn.close()

        # check grobid connection
        try:
            url = f'{GROBID_CONFIG['grobid_server']}/api/isalive'
            response = requests.get(url, timeout=2)
            if response.status_code != 200 or response.json() == False:
                return_data['errors'].append(f'ERROR: server GROBID tidak hidup di {url}. Periksa konfigurasi GROBID di docker.')
        except requests.exceptions.RequestException as e:
            return_data['errors'].append(f'ERROR: server GROBID tidak hidup di {url}. Jalankan GROBID di docker atau cek grobid.config.json')
    
    except:
        return return_data
    finally:
        return return_data


# ----- files from 'temp' directory -----
@app.route('/temp/pdf/<int:article_id>')
def get_pdf(article_id):
    try:
        return send_file(f'_temp/test_article/{article_id}.pdf')
    except:
        return ''
@app.route('/temp/tei/<int:article_id>')
def get_tei(article_id):
    try:
        with open(f'_temp/test_article/{article_id}.grobid.tei.xml', 'r') as tei:
            return tei.read()
    except:
        for f_name in os.listdir('_temp/test_article'):
            if f_name.startswith(str(article_id)) and f_name.endswith('.txt'):
                with open(f'_temp/test_article/{f_name}', 'r') as f:
                    return f'GROBID Error\n{f_name}\n{f.read()}'
        return ''


# ----- sample pdf from journal -----
@app.route('/test/journal/<int:journal_id>')
def get_sample_pdf(journal_id):

    print(f'Downloading random sample of 3 from journal_id={journal_id}')
    # clear_temp()
    return_data = { "log": [], "article_id": [] }

    # download sample pdf
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT article_id, location_file FROM articles WHERE journal_id = %s ORDER BY RAND() LIMIT 3', 
            (journal_id , )
            )
    
        for row in cursor.fetchall():
            id, url = row

            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                return_data['log'].append(f'HTTP error for article_id={id} in {url}')
                print(f'HTTP error for article_id={id} in {url}')
                continue

            if 'application/pdf' in response.headers.get('Content-Type', ''):
                file_path = f'{__dir__}/_temp/test_article/{id}.pdf'
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                return_data['log'].append(f'Downloaded: {id}.pdf from {url}')
                return_data['article_id'].append(id)
                print(f'Downloaded: {file_path} from {url}')
            else:
                return_data['log'].append(f'File for article_id={id} not found in {url}')
                print(f'File for article_id={id} not found in {url}')

    finally:
        conn.close()

    # parse with grobid
    print('Initialize GROBID')
    client = GrobidClient(config_path="./grobid.config.json")
    client.process("processReferences", f'{__dir__}\\_temp\\test_article', n=20, force=False)

    return return_data

# ----- sample pdf from article -----
@app.route('/test/article/<int:article_id>')
def get_sample_article(article_id):

    print(f'Downloading PDF with article_id={article_id}')
    return_data = { "log": [] }

    # download sample pdf
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT article_id, location_file FROM articles WHERE article_id = %s ORDER BY RAND() LIMIT 3', 
            (article_id , )
            )
    
        id, url = cursor.fetchone()

        try:
            response = requests.get(url)
            response.raise_for_status()
            if 'application/pdf' in response.headers.get('Content-Type', ''):
                file_path = f'{__dir__}/_temp/test_article/{id}.pdf'
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                return_data['log'].append(f'Downloaded: {id}.pdf from {url}')
                print(f'Downloaded: {file_path} from {url}')
            else:
                return_data['log'].append(f'File for article_id={id} not found in {url}')
                print(f'File for article_id={id} not found in {url}')

        except requests.exceptions.RequestException as e:
            return_data['log'].append(f'HTTP error for article_id={id} in {url}')
            print(f'HTTP error for article_id={id} in {url}')

    finally:
        conn.close()

    # parse with grobid
    print('Initialize GROBID')
    client = GrobidClient(config_path="./grobid.config.json")
    client.process("processReferences", f'{__dir__}\\_temp\\test_article', n=20, force=False)

    return return_data


if __name__ == "__main__":
    clear_temp()

    app.run(host=CONFIG['api_host'], port=CONFIG['api_port'])
    print(f'listening at {CONFIG['api_host']}:{CONFIG['api_port']}')
    print(f'open {__dir__}\\index.html on browser')