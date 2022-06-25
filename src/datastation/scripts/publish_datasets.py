import argparse
import os

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.ds_pidsfile import load_pids
from datastation.dv_api import publish_dataset


def publish_dataset_command(config, server_url, api_token, pids_file, type):
    pids = load_pids(pids_file)

    # Long delay because publish is doing a lot after the async. request is returning
    # and sometimes datasets get locked
    batch_process(pids, lambda pid: publish_dataset(server_url, api_token, pid, type), config['files']['output_dir'],
                  delay=5.0)


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Publishes datasets with the pids in the given inputfile')
    parser.add_argument('-p', '--pids_file', default='dataset_pids.txt', help='The input file with the dataset pids')
    parser.add_argument('-t', '--type', default='major',
                        help='The type of version upgrade, minor for metadata changes, otherwise major.')
    args = parser.parse_args()

    server_url = config['dataverse']['server_url']
    api_token = config['dataverse']['api_token']

    publish_dataset_command(config, server_url, api_token, args.pids_file, args.type)


if __name__ == '__main__':
    main()
