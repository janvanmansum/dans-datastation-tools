import argparse

import requests
from requests.auth import HTTPBasicAuth

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.ds_pidsfile import load_pids


def send_metadata_to_mds(config, doi, metadata):
    url = '%s/metadata/%s' % (config['datacite']['mds_endpoint'], doi)
    response = requests.put(
        url=url,
        auth=HTTPBasicAuth(config['datacite']['username'], config['datacite']['password']),
        headers={
            'Content-Type': 'application/xml;charset=UTF-8'
        },
        data=metadata)


def modify_registration_metadata(config, pid):
    url = '%s/api/datasets/:persistentId/modifyRegistrationMetadata?persistentId=%s' % (
        config['dataverse']['server_url'], pid)
    response = requests.post(
        url=url,
        headers={
            'X-Dataverse-key': config['dataverse']['api_token']
        }
    )
    print(response.text)


def update_datacite_record(config):
    def update_datacite_record_for_pid(pid):
        modify_registration_metadata(config, pid)
        return False

    return update_datacite_record_for_pid


def update_datacite_records(config, pid_file):
    pids = load_pids(pid_file)
    batch_process(pids, update_datacite_record(config), logging_dir='../work/', delay=1)


def main():
    config = init()

    parser = argparse.ArgumentParser(
        description='Downloads the DataCite metadata from Dataverse for a list of datasets and updates DataCite with '
                    'those records')
    parser.add_argument('dataset_pids', help='Newline separated file with dataset PIDs')
    args = parser.parse_args()
    update_datacite_records(config, args.dataset_pids)


if __name__ == '__main__':
    main()
