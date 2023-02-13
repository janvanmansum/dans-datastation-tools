import argparse
import logging
import csv
import re

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.dv_api import publish_dataset, get_dataset_metadata, change_access_request, change_file_restrict, \
    replace_dataset_metadata


def open_access_archeodepot(datasets_file, name_to_uri_file, dataverse_config, dry_run, delay):
    name_to_uri = {}
    with open(name_to_uri_file, "r") as input_file_handler:
        csv_reader = csv.DictReader(input_file_handler, delimiter=',')
        for row in csv_reader:
            name_to_uri[name_to_key(row["name"])] = row["url"]
    doi_to_license_name = {}
    with open(datasets_file, "r") as input_file_handler:
        csv_reader = csv.DictReader(input_file_handler, delimiter=',')
        for row in csv_reader:
            doi_to_license_name[row["DOI"]] = name_to_key(row["LICENSE_NAME"])
    batch_process(doi_to_license_name.items(),
                  lambda key_value: update(key_value[0], name_to_uri[key_value[1]], dry_run, dataverse_config),
                  delay)


def name_to_key(name):
    return re.sub("[- .]", "_", name)


def update(doi, uri, dry_run, dataverse_config):
    server_url = dataverse_config['server_url']
    api_token = dataverse_config['api_token']
    resp_data = get_dataset_metadata(server_url, api_token, doi)
    dirty = False
    if name_to_key(resp_data['license']['uri']) != uri:
        dirty = True
        json_data = '{"http://schema.org/license": "' + uri + '"}'
        logging.info(json_data)
        if not dry_run:
            replace_dataset_metadata(server_url, api_token, doi, json_data)
    if resp_data['fileAccessRequest']:
        logging.info("resetting access request")
        dirty = True
        if not dry_run:
            change_access_request(server_url, api_token, doi, False)
    for file in resp_data['files']:
        if file['restricted']:
            file_id = file['dataFile']['id']
            logging.info("resetting restrict {} {}".format(file_id, file['label']))
            dirty = True
            if not dry_run:
                change_file_restrict(server_url, api_token, file_id, False)
    logging.info('dirty = {} fileAccessRequest = {}, license = {}, rightsHolder = {}, TITLE = {}'
                 .format(dirty,
                         resp_data['fileAccessRequest'],
                         resp_data['license']['name'],
                         mdb_field_value(resp_data, 'dansRights', 'dansRightsHolder'),
                         mdb_field_value(resp_data, 'citation', 'title')))
    if dirty and not dry_run:
        logging.info('updating {}'.format(dry_run))
        publish_dataset(server_url, api_token, doi, 'updatecurrent')


def mdb_field_value(resp_data, metadata_block, field_name):
    return next(filter(lambda m: m['typeName'] == field_name,
                       resp_data['metadataBlocks'][metadata_block]['fields']
                       ))['value']


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Change archeodepot dataset to open access')
    parser.add_argument('-d', '--datasets', dest='datasets',
                        help='CSV file with: DOI, depositor(ignored), LICENSE_NAME')
    parser.add_argument('-l', '--licenses', dest='licenses',
                        help='CSV file with: uri, name')
    parser.add_argument('--delay', default=5.0,
                        help="Delay in seconds (because publish is doing a lot after the async. request is returning)")
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        help="only logs the actions, nothing is executed")

    args = parser.parse_args()
    open_access_archeodepot(args.datasets, args.licenses, config['dataverse'], args.dry_run,
                            float(args.delay))


if __name__ == '__main__':
    main()
