'''
DOCUMENTATION:

argv order  : <input_pdf_directory> <output_tei_directory>
description :
    extract all pdf inside <input_pdf_directory> references as tei/xml using grobid.
    each {filename}.pdf will be processed into {filename}.grobid.tei.xml inside
    <output_tei_directory>

changelog:
    - 27/02/2025: first release
    - 28/02/2025: fix absolute path error on GrobidClient's config_path
    - 01/03/2025: add makedirs before initializing grobid
'''

import os
import sys

from grobid_client.grobid_client import GrobidClient

# urutan: input_path, output_path
in_path, out_path = sys.argv[1:]

__dir__ = os.path.dirname(os.path.abspath(__file__))

os.makedirs(out_path, exist_ok=True)

client = GrobidClient(config_path=f"{__dir__}/grobid.config.json")
client.process(
    service="processReferences", 
    input_path=in_path,
    output=out_path,
    include_raw_citations=True,
    n=20,
    force=False,
    verbose=True
)