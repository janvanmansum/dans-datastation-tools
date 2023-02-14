import argparse
import json
import logging
import csv
import re

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.dv_api import publish_dataset, get_dataset_metadata, change_access_request, change_file_restrict, \
    replace_dataset_metadata


def open_access_archeodepot(datasets_file, licenses_file, dag_raporten_file, dataverse_config, dry_run, delay):
    rights_holder_to_license_uri = {}
    with open(licenses_file, "r") as input_file_handler:
        csv_reader = csv.DictReader(input_file_handler, delimiter=',')
        for row in csv_reader:
            rights_holder_to_license_uri[to_key(row["RIGHTS_HOLDER"])] = row["URI"]
    doi_to_license_uri = {}
    with open(datasets_file, "r") as input_file_handler:
        csv_reader = csv.DictReader(input_file_handler, delimiter=',', fieldnames=["DOI"], restkey="rest")
        for row in csv_reader:
            key = to_key(row["rest"][-1].strip())
            uri = rights_holder_to_license_uri.get(key, "")
            if uri:
                doi_to_license_uri[row["DOI"]] = uri
            else:
                logging.warning("no license for line {}: {}".format(csv_reader.line_num, row))
    doi_to_dag_raporten = {}
    with open(dag_raporten_file, "r") as input_file_handler:
        csv_reader = csv.DictReader(input_file_handler, delimiter=',',
                                    fieldnames=["dataset_id", "DOI"], restkey="files")
        next(csv_reader)
        for row in csv_reader:
            doi_to_dag_raporten[to_key(row["DOI"])] = list(filter(lambda item: item != "", row["files"]))
    batch_process(doi_to_license_uri.items(),
                  lambda key_value: update("doi:"+key_value[0],
                                           key_value[1],
                                           doi_to_dag_raporten.get(to_key(key_value[0]), []),
                                           dry_run,
                                           dataverse_config),
                  delay)


def to_key(name):
    return re.sub("[^a-zA-Z0-1]", "_", name)


def update(doi, uri, dag_raporten, dry_run, dataverse_config):
    server_url = dataverse_config['server_url']
    api_token = dataverse_config['api_token']
    resp_data = get_dataset_metadata(server_url, api_token, doi)
    dirty = False
    if resp_data['license']['uri'] != uri:
        dirty = True
        json_data = json.dumps({"http://schema.org/license": uri})
        logging.info(json_data)
        if not dry_run:
            replace_dataset_metadata(server_url, api_token, doi, json_data)
    has_dag_raporten = not dag_raporten
    if resp_data['fileAccessRequest'] or has_dag_raporten:
        logging.info("(re)setting access request {}".format(has_dag_raporten))
        dirty = True
        if not dry_run:
            change_access_request(server_url, api_token, doi, json.dumps(has_dag_raporten))
    for file in resp_data['files']:
        path = re.sub("^/", "", file.get('directoryLabel', "") + "/" + file['label'])
        is_dag_raport = path in dag_raporten
        if is_dag_raport and not resp_data["termsOfAccess"]:
            logging.warning("no terms of access, can't restrict {} {}".format(doi, path))
        elif file['restricted'] != is_dag_raport:
            file_id = file['dataFile']['id']
            logging.info("setting restrict to {} for {} {}".format(is_dag_raport, file_id, file['label']))
            dirty = True
            if not dry_run:
                change_file_restrict(server_url, api_token, file_id, json.dumps(is_dag_raport))
    logging.info('dirty = {} fileAccessRequest = {}, license = {}, rightsHolder = {}, TITLE = {}'
                 .format(dirty,
                         resp_data['fileAccessRequest'],
                         resp_data['license']['name'],
                         mdb_field_value(resp_data, 'dansRights', 'dansRightsHolder'),
                         mdb_field_value(resp_data, 'citation', 'title')))
    if dirty and not dry_run:
        logging.info('publish_dataset')
        publish_dataset(server_url, api_token, doi, 'updatecurrent')


def mdb_field_value(resp_data, metadata_block, field_name):
    return next(filter(lambda m: m['typeName'] == field_name,
                       resp_data['metadataBlocks'][metadata_block]['fields']
                       ))['value']


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Change archeodepot dataset to open access')
    parser.add_argument('-d', '--datasets', dest='datasets',
                        help='CSV file (solr query result) with DOI, ... , rights-holder.')
    parser.add_argument('-r', '--dag-raporten', dest='dag_raporten',
                        help='CSV file with: easy-id, DOI, File1, File2...')
    parser.add_argument('-l', '--licenses', dest='licenses',
                        help='CSV file with: uri, name. N.B. no trailing slash for the uri')
    parser.add_argument('--delay', default=5.0,
                        help="Delay in seconds (because publish is doing a lot after the async. request is returning)")
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        help="only logs the actions, nothing is executed")

    args = parser.parse_args()
    open_access_archeodepot(args.datasets, args.licenses, args.dag_raporten, config['dataverse'], args.dry_run,
                            float(args.delay))


if __name__ == '__main__':
    main()
