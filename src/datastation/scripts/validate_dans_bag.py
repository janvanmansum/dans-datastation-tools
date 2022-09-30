import argparse
import json
import logging
import os
import csv
from email import encoders
from email.mime.application import MIMEApplication

import requests
import typing
import yaml

from datastation.config import init
from email.mime.multipart import MIMEMultipart


def validate_dans_bag(path, package_type, level, validator_url, accept_json, is_dry_run, output_writer, is_first=True):
    command = {
        'bagLocation': os.path.abspath(path),
        'packageType': package_type,
        'level': level
    }

    msg = MIMEMultipart("form-data")
    p = MIMEApplication(json.dumps(command), "json", _encoder=encoders.encode_noop)
    p.add_header("Content-Disposition", "form-data; name=command")
    msg.attach(p)

    body = msg.as_string().split('\n\n', 1)[1]
    headers = dict(msg.items())
    headers.update({'Accept': 'application/json' if accept_json else 'text/plain'})

    if is_dry_run:
        logging.info("Only printing command, not sending it...")
        print(msg.as_string())
    else:
        r = requests.post('{}/validate'.format(validator_url), data=body,
                          headers=headers)
        print(r.text)
        if accept_json:
            result = json.loads(r.text)
        else:
            result = yaml.safe_load(r.text)

        output_writer(result, is_first)

    return 0


def validate_dans_bag_in_deposit(path, package_type, level, validator_url, accept_json, is_dry_run, output_writer,
                                 is_first=True):
    subdirs = get_subdirs(path)
    if len(subdirs) == 1:
        validate_dans_bag(subdirs[0], package_type, level, validator_url, accept_json, is_dry_run, output_writer,
                          is_first)
    else:
        print("ERROR: deposit found with {} subdirectories. There should be exactly one".format(len(subdirs)))


def get_subdirs(dir):
    return list(filter(lambda d: os.path.isdir(d), map(lambda d: os.path.join(dir, d), os.listdir(dir))))


def validate_command(path, package_type, level, service_baseurl, accept_json, dry_run, output_writer):
    if os.path.exists("{}/bagit.txt".format(path)):
        logging.info("Found one bag at {}".format(path))
        validate_dans_bag(path, package_type, level, service_baseurl, accept_json, dry_run, output_writer)
    elif os.path.exists("{}/deposit.properties".format(path)):
        logging.info("Found a deposit at {}".format(path))
        validate_dans_bag_in_deposit(path, package_type, level, service_baseurl, accept_json, dry_run, output_writer)
    else:
        logging.info("Not a bag or a deposit, assuming batch of deposits")
        subdirs = get_subdirs(path)
        logging.info("Found {} deposits to validate".format(len(subdirs)))
        is_first = True
        for d in subdirs:
            logging.debug("Validating {}".format(d))
            validate_dans_bag_in_deposit(d, package_type, level, service_baseurl, accept_json,
                                         dry_run, output_writer, is_first)
            is_first = False


def create_csv_result_writer(csv_writer: csv.DictWriter):
    def result_writer(result, is_first: bool):
        csv_writer.writerow({
            'DEPOSIT': result["Bag location"],
            'BAG': result["Name"],
            'COMPLIANT': result["Is compliant"],
            'RULE VIOLATIONS': result["Rule violations"]
        })

    return result_writer


def create_json_result_writer(f: typing.TextIO):
    def result_writer(result, is_first: bool):
        if not is_first:
            f.write(", ")
        f.write(json.dumps(result))

    return result_writer


def create_yaml_result_writer(f: typing.TextIO):
    def result_writer(result, is_first: bool):
        f.write(yaml.dump([result]))

    return result_writer


def main():
    config = init()
    default_info_package_type = config['dans_bag_validator']['default_information_package_type']

    parser = argparse.ArgumentParser(
        description='Validate one or more bags to see if they comply with the DANS BagIt Profile v1')
    parser.add_argument('path', metavar='<batch-or-deposit-or-bag>',
                        help='Directory containing a bag, a deposit or a batch of deposits')
    parser.add_argument('-t', '--information-package-type', dest='info_package_type',
                        help='Which information package type to validate this bag as',
                        choices=['DEPOSIT', 'MIGRATION'],
                        default=default_info_package_type)
    parser.add_argument('-l', '--level', dest='level', help='Level of validation',
                        choices=['STAND-ALONE', 'WITH-DATA-STATION-CONTEXT'],
                        default='STAND-ALONE')
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                        help='Only print command to be sent to server, but do not actually send it')
    parser.add_argument('-o', '--out-file', dest='out_file',
                        required=True,
                        help='Output file to save results to. If the file name ends in .csv the output is saved as CSV, '
                             'if .json as JSON and otherwise as Yaml')

    args = parser.parse_args()
    service_baseurl = config['dans_bag_validator']['service_baseurl']
    package_type = args.info_package_type
    level = args.level
    dry_run = args.dry_run
    path = args.path

    with(open(args.out_file, 'w')) as f:
        if args.out_file.endswith('.csv'):
            fieldnames = ['DEPOSIT', 'BAG', 'COMPLIANT', 'RULE VIOLATIONS']
            csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
            csv_writer.writeheader()
            validate_command(path, package_type, level, service_baseurl, accept_json=True, dry_run=dry_run,
                             output_writer=create_csv_result_writer(csv_writer))
        else:
            accept_json = args.out_file.endswith('.json')
            try:
                if accept_json:
                    f.write("[")
                validate_command(path, package_type, level, service_baseurl, accept_json, dry_run,
                                 create_json_result_writer(f) if accept_json else create_yaml_result_writer(f))
            finally:
                if accept_json:
                    f.write("]")


if __name__ == '__main__':
    main()
