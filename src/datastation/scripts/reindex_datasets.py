import argparse
import os

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.ds_pidsfile import load_pids
from datastation.dv_api import reindex_dataset


def reindex_dataset_command(config, server_url, pids_file):
    # look for inputfile in configured OUTPUT_DIR
    full_name = os.path.join(config['files']['output_dir'], pids_file)
    pids = load_pids(full_name)

    # could be fast, but depends on number of files inside the dataset
    batch_process(pids, lambda pid: reindex_dataset(server_url, pid), config['files']['output_dir'], delay=1.5)


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Reindex datasets with the pids in the given inputfile')
    parser.add_argument('-p', '--pids_file', default='dataset_pids.txt', help='The input file with the dataset pids')
    args = parser.parse_args()

    server_url = config['dataverse']['server_url']

    reindex_dataset_command(config, server_url, args.pids_file)


if __name__ == '__main__':
    main()
