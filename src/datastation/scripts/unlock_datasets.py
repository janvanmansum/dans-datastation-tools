import argparse
import os
import json

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.ds_pidsfile import load_pids

from datastation.dv_api import get_dataset_locks, delete_dataset_locks


def unlock_dataset_action(server_url, api_token, pid):
    deleted_locks = False
    resp_data = get_dataset_locks(server_url, pid)
    # print(json.dumps(resp_data, indent=2))
    if len(resp_data) == 0:
        print("No locks")
        print("Leave as-is")
    else:
        print("Found locks")
        print(json.dumps(resp_data, indent=2))
        # delete
        print("Try deleting the locks")
        delete_dataset_locks(server_url, api_token, pid)
        print("Done")
        deleted_locks = True

    return deleted_locks


def unlock_dataset_command(config, pids_file):
    full_name = os.path.join(config['files']['output_dir'], pids_file)
    pids = load_pids(full_name)

    # could be fast, but depends on number of files inside the dataset
    batch_process(pids,
                  lambda pid: unlock_dataset_action(config['dataverse']['server_url'], config['dataverse']['api_token'],
                                                    pid), config['files']['output_dir'], delay=1.5)


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Unlock datasets (if locked) with the pids in the given input file')
    parser.add_argument('-p', '--pids-file', default='dataset_pids.txt', help='The input file with the dataset pids')
    args = parser.parse_args()
    unlock_dataset_command(config, args.pids_file)


if __name__ == '__main__':
    main()
