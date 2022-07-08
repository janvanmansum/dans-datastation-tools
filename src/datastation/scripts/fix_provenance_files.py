import argparse, logging
import os.path

from datastation.config import init


def conforms_to_schema(path):
    return True


def is_provenance_file(path):
    # with open(path) as stream:
    return True


def process_dataset(file_storage_root, doi, storage_identifier, current_checksum, dvobject_id):
    logging.debug("({}, {}, {}, {})".format(doi, storage_identifier, current_checksum, dvobject_id))
    provenance_path = os.path.join(file_storage_root, doi, storage_identifier)
    # if (os.path.exists(provenance_path)):
    #     if is_provenance_file(provenance_path):


def main():
    config = init()

    parser = argparse.ArgumentParser(
        description='Fixes one or more invalid provenance.xml files. With the optional parameters, it is possible to process one dataset/provenance.xml.'
                    + ' If none of the optional parameters is provided the standard input is expected to contain a CSV file with the columns: DOI, STORAGE_IDENTIFIER, CURRENT_SHA1_CHECKSUM and DVOBJECT_ID')
    parser.add_argument('-d', '--doi', dest='doi', help='the dataset DOI')
    parser.add_argument('-s', '--storage-identifier', dest='storage_identifier',
                        help='the storage identifier of the provenance.xml file')
    parser.add_argument('-c', '--current-sha1-checksum', dest='current_sha1_checksum',
                        help='the expected current checksum of the provenance.xml file')
    parser.add_argument('-o', '--dvobject-id', dest='dvobject_id',
                        help='the dvobject.id for the provenance.xml in dvndb')
    args = parser.parse_args()

    process_dataset(config['dataverse']['files_root'], args.doi, args.storage_identifier, args.current_sha1_checksum,
                    args.dvobject_id)


if __name__ == '__main__':
    main()
