inisialisasi:
- modul pip yang dibutuhkan: flask, flask-cors, grobid-client-python
- jalankan GROBID di docker, konfirmasi portnya, cocokkan dengan grobid.config.json
- konfirmasi konfigurasi database di config.json
- apabila belum ada, import tabel 'grobid_references' ke database


dokumentasi:
- test journals:
    1. mendownload 3 pdf acak dari journal_id di folder _temp/test_article
    2. jalankan processReference oleh grobid
    3. tampilkan di GUI

- batch download journals:
    1. cek apakah artikel dengan journal_id tersebut sudah ada di tabel 'grobid_references'
    2. apabila belum, copy semua record di 'articles' dengan journal_id tersebut ke 'grobid_references'
    3. bagi pipeline menjadi n worker, masing-masing mengurusi download dengan article_id % n = i 
    4. update record di 'grobid_references' sesuai apakah download berhasil atau tidak