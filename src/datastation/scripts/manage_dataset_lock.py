import argparse
import logging
import json

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.ds_pidsfile import load_pids

from datastation.dv_api import get_dataset_locks, delete_dataset_locks_all, delete_dataset_lock, create_dataset_lock


def dataset_lock_action(server_url, api_token, pid, action, lock_type):
    if action == "unlock":
        if lock_type:
            delete_lock_type(server_url, api_token, pid, lock_type)
        else:
            delete_all_locks(server_url, api_token, pid)
    elif action == "show":
        show_all_locks(server_url, pid)
    elif action == "lock":
        create_lock(server_url, api_token, pid, lock_type)


def create_lock(server_url, api_token, pid, lock_type):
    # check the lock doesn't exist?
    create_dataset_lock(server_url, api_token, pid, lock_type)


def show_all_locks(server_url, pid):
    resp_data = get_dataset_locks(server_url, pid)
    if len(resp_data) == 0:
        logging.info("{} - No locks found".format(pid))
    else:
        logging.info(json.dumps(resp_data, indent=2))


def delete_lock_type(server_url, api_token, pid, lock_type):
    deleted_lock = False
    resp_data = get_dataset_locks(server_url, pid)
    if len(resp_data) == 0:
        logging.debug("{} - No locks found, leave as-is".format(pid))
    else:
        logging.info("{} - Found locks".format(pid))
        logging.debug(json.dumps(resp_data, indent=2))
        logging.debug("{} - Try deleting the locks".format(pid))
        delete_dataset_lock(server_url, api_token, pid, lock_type)
        deleted_lock = True

    return deleted_lock


def delete_all_locks(server_url, api_token, pid):
    deleted_locks = False
    resp_data = get_dataset_locks(server_url, pid)
    if len(resp_data) == 0:
        logging.debug("{} - No locks found, leave as-is".format(pid))
    else:
        logging.info("{} - Found locks".format(pid))
        logging.debug(json.dumps(resp_data, indent=2))
        logging.debug("{} - Try deleting the locks".format(pid))
        delete_dataset_locks_all(server_url, api_token, pid)
        deleted_locks = True

    return deleted_locks


def unlock_dataset_command(server_url, api_token, delay, pids_file, action, lock_type):
    # could be fast, but depends on number of files inside the dataset
    batch_process(load_pids(pids_file),
                  lambda pid: dataset_lock_action(server_url, api_token, pid, action, lock_type), delay)


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Manage locks of datasets with the pids in the given input file. '
                                                 'Locking and unlocking requires superuser privileges.')
    parser.add_argument('-a', '--action', dest='action', choices=["show", "lock", "unlock"],
                        help="the action to be taken: lock, unlock, show")
    parser.add_argument('-d', '--datasets', dest='pids_file', help='The input file with the dataset pids')
    parser.add_argument('-t', '--lock-type', dest='lock_type',
                        choices=["Ingest", "Workflow", "InReview", "DcmUpload", "finalizePublication", "EditInProgress",
                                 "FileValidationFailed"], help='The lock type to (un)lock for the datasets')
    parser.add_argument('--delay', default=1.5, help="Delay in seconds")
    args = parser.parse_args()

    server_url = config['dataverse']['server_url']
    api_token = config['dataverse']['api_token']

    unlock_dataset_command(server_url, api_token, args.delay, args.pids_file, args.action, args.lock_type)


if __name__ == '__main__':
    main()
