import argparse
import json
import logging
import csv
import re

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.dv_api import publish_dataset, get_dataset_metadata, change_access_request, replace_dataset_metadata, \
    change_file_restrict


def open_access_archeodepot(datasets_file, licenses_file, keep_restricted_files, dataverse_config, dry_run, delay):
    doi_to_license_uri = read_doi_to_license(datasets_file, read_rights_holder_to_license(licenses_file))
    doi_to_keep_restricted = read_doi_to_keep_restricted(keep_restricted_files)
    server_url = dataverse_config['server_url']
    api_token = dataverse_config['api_token']
    logging.debug("is dry run: {}".format(dry_run))
    batch_process(doi_to_license_uri.items(),
                  lambda doi_to_license: update_license("doi:" + doi_to_license[0],
                                                        doi_to_license[1],
                                                        doi_to_keep_restricted.get(to_key(doi_to_license[0]), []),
                                                        server_url,
                                                        api_token,
                                                        dry_run),
                  delay)


def read_doi_to_license(datasets_file, rights_holder_to_license_uri):
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
    return doi_to_license_uri


def read_doi_to_keep_restricted(keep_restricted_files):
    doi_to_keep_restricted = {}
    with open(keep_restricted_files, "r") as input_file_handler:
        csv_reader = csv.DictReader(input_file_handler, delimiter=',',
                                    fieldnames=["dataset_id", "DOI"], restkey="files")
        next(csv_reader)
        for row in csv_reader:
            doi_to_keep_restricted[to_key(row["DOI"])] = list(filter(lambda item: item != "", row["files"]))
    return doi_to_keep_restricted


def read_rights_holder_to_license(licenses_file):
    rights_holder_to_license_uri = {}
    with open(licenses_file, "r") as input_file_handler:
        csv_reader = csv.DictReader(input_file_handler, delimiter=',')
        for row in csv_reader:
            rights_holder_to_license_uri[to_key(row["RIGHTS_HOLDER"])] = row["URI"]
    return rights_holder_to_license_uri


def to_key(name):
    return re.sub("[^a-zA-Z0-1]", "_", name)


def update_license(doi, uri, dag_rapporten, server_url, api_token, dry_run):
    resp_data = get_dataset_metadata(server_url, api_token, doi)
    dirty = False
    if resp_data['license']['uri'] != uri:
        dirty = True
        json_data = json.dumps({"http://schema.org/license": uri})
        logging.info(json_data)
        if not dry_run:
            replace_dataset_metadata(server_url, api_token, doi, json_data)
    accessible_dag_rapporten = list(filter(
        lambda file: not file['restricted'] and file_path(file) in dag_rapporten,
        resp_data['files']))
    restricted_other_files = list(filter(
        lambda file: file['restricted'] and file_path(file) not in dag_rapporten,
        resp_data['files']))
    logging.info("number of: dag_rapporten={}, accessible_dag_rapporten={}, restricted_other_files={}; {}".format(
        len(dag_rapporten), len(accessible_dag_rapporten), len(restricted_other_files), dag_rapporten))
    has_accessible_dag_rapporten = len(accessible_dag_rapporten) > 0
    has_dag_rapporten = len(dag_rapporten) > 0
    if bool(resp_data['fileAccessRequest']) != has_dag_rapporten:
        logging.info("(re)setting access request {}".format(has_dag_rapporten))
        dirty = True
        if not dry_run:
            change_access_request(server_url, api_token, doi, has_dag_rapporten)
    change_file_restriction(False, restricted_other_files, server_url, api_token, dry_run)
    if has_accessible_dag_rapporten:
        if not resp_data.get("termsOfAccess", None):
            logging.warning("no terms of access, can't restrict dag-rapporten of {}".format(doi))
        else:
            change_file_restriction(True, accessible_dag_rapporten, server_url, api_token, dry_run)
    logging.info('dirty = {} fileAccessRequest = {}, license = {}, rightsHolder = {}, title = {}'
                 .format(dirty,
                         resp_data['fileAccessRequest'],
                         resp_data['license']['name'],
                         mdb_field_value(resp_data, 'dansRights', 'dansRightsHolder'),
                         mdb_field_value(resp_data, 'citation', 'title')))
    if dirty and not dry_run:
        logging.info(doi + ' publish_dataset')
        publish_dataset(server_url, api_token, doi, 'updatecurrent')


def file_path(file_item):
    return re.sub("^/", "", file_item.get('directoryLabel', "") + "/" + file_item['label'])


def change_file_restriction(restrictedValue, files, server_url, api_token, dry_run):
    if len(files) > 0:
        file_ids = list(map(lambda file: file['dataFile']['id'], files))
        logging.info("dry_run={}; set restricted={} for ({})".format(dry_run, restrictedValue, file_ids))
        if not dry_run:
            for file_id in file_ids:
                logging.debug("updating {}".format(file_id))
                change_file_restrict(server_url, api_token, file_id, restrictedValue)


def mdb_field_value(resp_data, metadata_block, field_name):
    return next(filter(lambda m: m['typeName'] == field_name,
                       resp_data['metadataBlocks'][metadata_block]['fields']
                       ))['value']


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Change archeodepot dataset to open access')
    parser.add_argument('-d', '--datasets', dest='datasets',
                        help='CSV file (solr query result) header: DOI, ..., RIGHTS_HOLDER')
    parser.add_argument('-r', '--dag-rapporten', dest='dag_rapporten',
                        help='CSV file with header: dataset_id, DOI, File1, File2... N.B. The DOI is just the id, not a uri')
    parser.add_argument('-l', '--licenses', dest='licenses',
                        help='CSV file with: uri, name. N.B. no trailing slash for the uri')
    parser.add_argument('--delay', default=5.0,
                        help="Delay in seconds (publish does a lot after the asynchronous request is returning)")
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        help="only logs the actions, nothing is executed")

    args = parser.parse_args()
    open_access_archeodepot(args.datasets, args.licenses, args.dag_rapporten, config['dataverse'], args.dry_run,
                            float(args.delay))


if __name__ == '__main__':
    main()
