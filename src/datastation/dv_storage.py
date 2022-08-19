import logging
import os.path
from uuid import uuid4
from datetime import datetime
from os import walk, path
from shutil import copy


# Taken from edu.harvard.iq.dataverse.DataFileServiceBean#generateStorageIdentifier()
def generate_storage_identifier():
    uuid = str(uuid4())
    hexRandom = uuid[-12:]
    hexTimestamp = hex(int(datetime.now().timestamp() * 1000))[2:]  # remove 0x from beginning
    return "{}-{}".format(hexTimestamp, hexRandom)

def file_json_data_creator(relative_path, filename):
    return {
        "directoryLabel": "",
        "fileName": "",
        "description": "",
        "categories": [],
        "restrict": "false",
        "storageIdentifier": "",
        "mimeType": "application/octet-stream",
        "checksum": {
            "@type": "SHA-1",
            "@value": ""
        }
    }

def prestage_file(fileroot, doi, f):
    storage_id = generate_storage_identifier()
    dest = path.join(fileroot, doi, storage_id)
    logging.debug("Copying {} to {}".format(f, dest))
    copy(f, dest)

def prestage_files(fileroot, doi, dir):
    for root, _, files in walk(dir):
        for f in files:
            prestage_file(fileroot, doi, os.path.join(root, f))

def ensure_doi_directory_exists(fileroot, doi):
    doi_dir = path.join(fileroot, doi)
    if os.path.isdir(doi_dir):
        logging.debug("DOI directory already exists: {}".format(doi_dir))
    else:
        logging.info("Creating new DOI directory: {}".format(doi_dir))
        os.makedirs(doi_dir)