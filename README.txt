requirements:
- modul pip yang dibutuhkan: flask, flask-cors, grobid-client-python
- MySQL (bisa dari XAMPP) yang sudah terdapat data GARUDA

inisialisasi:
- jalankan GROBID di docker, konfirmasi portnya, cocokkan dengan grobid.config.json
- jalankan MySQL dari XAMPP
- konfirmasi konfigurasi database di config.json
- apabila belum ada, import tabel 'grobid_references.sql' ke database
- jalankan main.py

dokumentasi algoritma:
- test journals:
    1. mendownload 3 pdf acak dari journal_id di folder _temp/test_article
    2. jalankan processReference oleh grobid
    3. tampilkan di GUI

- batch_download_by_journals.py
    1. cek apakah artikel dengan journal_id tersebut sudah ada di tabel 'grobid_references'
    2. apabila belum, copy semua record di 'articles' dengan journal_id tersebut ke 'grobid_references'
    3. bagi pipeline menjadi n worker, masing-masing mengurusi download dengan article_id % n = i 
    4. update record di 'grobid_references' sesuai apakah download berhasil atau tidak

- batch_extract_tei_reference.py
    - ekstraksi semua pdf dalam input_pdf_directory oleh GROBID menjadi TEI/XML di output_tei_directory

- batch_tei_to_database.py
    1. query ke 'grobid_references' untuk pdf_downloaded=1 AND pdf_processed=0
    2. untuk tiap record, cek apakah file TEI/XML ada
    3. update di database 