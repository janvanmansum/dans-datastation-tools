import argparse

from datastation.config import init

def main():
    config = init()

    parser = argparse.ArgumentParser(
        description='Fixes one or more invalid provenance.xml files')
    parser.add_argument('-d', '--doi', help='the dataset DOI')
    parser.add_argument('-s', '--storage-identifier', help='the storage identifier of the provenance.xml file')
    parser.add_argument('-c', '--current-sha1-checksum', help='the expected current checksum of the provenance.xml file')
    parser.add_argument('-o', '--dvobject-id', help='the dvobject.id for the provenance.xml in dvndb')
    args = parser.parse_args()



if __name__ == '__main__':
    main()