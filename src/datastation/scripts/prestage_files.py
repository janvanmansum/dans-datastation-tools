import argparse
import os.path
import sys

from datastation.config import init
from datastation.dv_storage import prestage_file, prestage_files, ensure_doi_directory_exists


def main():
    config = init()

    parser = argparse.ArgumentParser(
        description='Prestages files in the Dataverse storage directory')
    parser.add_argument('-d', '--doi', dest='doi', help='the dataset DOI')
    parser.add_argument('file',
                        help='file to prestage; if it is a directory, all files in it will be prestaged recursively')
    args = parser.parse_args()

    file_or_dir = args.file
    if not os.path.exists(file_or_dir):
        print('File or directory not found: {}'.format(file_or_dir), file=sys.stderr)
        exit(1)

    ensure_doi_directory_exists(config['dataverse']['files_root'], args.doi)
    if os.path.isfile(file_or_dir):
        prestage_file(config['dataverse']['files_root'], args.doi, file_or_dir)
    elif os.path.isdir(file_or_dir):
        prestage_files(config['dataverse']['files_root'], args.doi, file_or_dir)


if __name__ == '__main__':
    main()
