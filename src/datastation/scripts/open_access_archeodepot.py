import argparse
import json
import logging
import csv
import re

import psycopg

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.dv_api import publish_dataset, get_dataset_metadata, change_access_request, replace_dataset_metadata


def open_access_archeodepot(datasets_file, licenses_file, dag_raporten_file, dataverse_config, dry_run, delay):
    doi_to_license_uri = read_doi_to_license(datasets_file, read_rights_holder_to_license(licenses_file))
    doi_to_dag_raporten = read_doi_to_dag_raporten(dag_raporten_file)
    server_url = dataverse_config['server_url']
    api_token = dataverse_config['api_token']
    dvndb_conn = None
    logging.debug("is dry run: {}".format(dry_run))
    try:
        if not dry_run:
            logging.debug("connecting to DB")
            dvndb_conn = connect_to_dvndb(dataverse_config)
        batch_process(doi_to_license_uri.items(),
                      lambda key_value: update("doi:" + key_value[0],
                                               key_value[1],
                                               doi_to_dag_raporten.get(to_key(key_value[0]), []),
                                               server_url,
                                               api_token,
                                               dvndb_conn),
                      delay)
    finally:
        if dvndb_conn:
            dvndb_conn.close()


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


def read_doi_to_dag_raporten(dag_raporten_file):
    doi_to_dag_raporten = {}
    with open(dag_raporten_file, "r") as input_file_handler:
        csv_reader = csv.DictReader(input_file_handler, delimiter=',',
                                    fieldnames=["dataset_id", "DOI"], restkey="files")
        next(csv_reader)
        for row in csv_reader:
            doi_to_dag_raporten[to_key(row["DOI"])] = list(filter(lambda item: item != "", row["files"]))
    return doi_to_dag_raporten


def read_rights_holder_to_license(licenses_file):
    rights_holder_to_license_uri = {}
    with open(licenses_file, "r") as input_file_handler:
        csv_reader = csv.DictReader(input_file_handler, delimiter=',')
        for row in csv_reader:
            rights_holder_to_license_uri[to_key(row["RIGHTS_HOLDER"])] = row["URI"]
    return rights_holder_to_license_uri


def connect_to_dvndb(dataverse_config):
    return psycopg.connect("host={} dbname={} user={} password={}".format(
        dataverse_config['db']['host'],
        dataverse_config['db']['dbname'],
        dataverse_config['db']['user'],
        dataverse_config['db']['password']))


def to_key(name):
    return re.sub("[^a-zA-Z0-1]", "_", name)


def update(doi, uri, dag_raporten, server_url, api_token, dvndb_conn):
    resp_data = get_dataset_metadata(server_url, api_token, doi)
    dirty = False
    if resp_data['license']['uri'] != uri:
        dirty = True
        json_data = json.dumps({"http://schema.org/license": uri})
        logging.info(json_data)
        if dvndb_conn:
            replace_dataset_metadata(server_url, api_token, doi, json_data)
    accessible_dag_raporten = filter(
        lambda file: not file['restricted'] and file_path(file) in dag_raporten,
        resp_data['files'])
    restricted_other_files = filter(
        lambda file: file['restricted'] and not file_path(file) in dag_raporten,
        resp_data['files'])
    has_dag_raporten = not dag_raporten
    if resp_data['fileAccessRequest'] or has_dag_raporten:
        logging.info("(re)setting access request {}".format(has_dag_raporten))
        dirty = True
        if dvndb_conn:
            change_access_request(server_url, api_token, doi, json.dumps(has_dag_raporten))
    # TODO start DB transaction
    change_file_restrict(False, restricted_other_files, dvndb_conn)
    if accessible_dag_raporten:
        if not resp_data.get("termsOfAccess", None):
            logging.warning("no terms of access, can't restrict dag-raporten of {}".format(doi))
        else:
            change_file_restrict(True, accessible_dag_raporten, dvndb_conn)
    logging.info('dirty = {} fileAccessRequest = {}, license = {}, rightsHolder = {}, TITLE = {}'
                 .format(dirty,
                         resp_data['fileAccessRequest'],
                         resp_data['license']['name'],
                         mdb_field_value(resp_data, 'dansRights', 'dansRightsHolder'),
                         mdb_field_value(resp_data, 'citation', 'title')))
    if dirty and dvndb_conn:
        logging.info('publish_dataset')
        publish_dataset(server_url, api_token, doi, 'updatecurrent')
    # TODO commit DB transaction (or roll back on failure?)


def file_path(file_item):
    return re.sub("^/", "", file_item.get('directoryLabel', "") + "/" + file_item['label'])


def change_file_restrict(value, files, dvndb_conn):
    ids = ",".join(map(str, list(map(lambda file: file['dataFile']['id'], files))))
    if ids:
        q = "update datafile set restricted = {} where id in ({})".format(str(value), ids)
        logging.info(q)
        if dvndb_conn:
            try:
                dvndb_conn.execute(q)
            except psycopg.DatabaseError:
                logging.error("FATAL ERROR on: " + q)
                raise


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
