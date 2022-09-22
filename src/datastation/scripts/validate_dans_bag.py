import argparse
import json
import logging
import os
from email import encoders
from email.mime.application import MIMEApplication

import requests

from datastation.config import init
from email.mime.multipart import MIMEMultipart


def validate_dans_bag(path, package_type, level, validator_url, accept_json, is_dry_run):
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
        print('Server responded: %s' % r.text)

    return 0


def validate_dans_bag_in_deposit(path, package_type, level, validator_url, accept_json, is_dry_run):
    subdirs = get_subdirs(path)
    if len(subdirs) == 1:
        validate_dans_bag(subdirs[0], package_type, level, validator_url, accept_json, is_dry_run)
    else:
        print("ERROR: deposit found with {} subdirectories. There should be exactly one".format(len(subdirs)))


def get_subdirs(dir):
    return list(filter(lambda d: os.path.isdir(d), map(lambda d: os.path.join(dir, d), os.listdir(dir))))


def main():
    config = init()
    parser = argparse.ArgumentParser(
        description='Validate one or more bags to see if they comply with the DANS BagIt Profile v1')
    parser.add_argument('path', metavar='<batch-or-deposit-or-bag>',
                        help='Directory containing a bag, a deposit or a batch of deposits')
    parser.add_argument('-m', '--migration', dest='is_migration', action='store_true',
                        help='Validate the bag as a migration')
    parser.add_argument('-c', '--with-datastation-context', dest='in_context', action='store_true',
                        help='Validate in Data Station context')
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                        help='Only print command to be sent to server, but do not actually send it')
    parser.add_argument('-j', '--json', dest='accept_json', action='store_true',
                        help='Ask the server to return JSON instead of Yaml')

    args = parser.parse_args()
    service_baseurl = config['dans_bag_validator']['service_baseurl']
    package_type = "MIGRATION" if args.is_migration else "DEPOSIT"
    level = "WITH-DATA-STATION-CONTEXT" if args.in_context else "STAND-ALONE"
    dry_run = args.dry_run

    path = args.path

    if os.path.exists("{}/bagit.txt".format(path)):
        logging.info("Found one bag at {}".format(path))
        validate_dans_bag(path, package_type, level, service_baseurl, args.accept_json, dry_run)
    elif os.path.exists("{}/deposit.properties".format(path)):
        logging.info("Found a deposit at {}".format(path))
        validate_dans_bag_in_deposit(path, package_type, level, service_baseurl, args.accept_json, dry_run)
    else:
        logging.info("Not a bag or a deposit, assuming batch of deposits")
        subdirs = get_subdirs(path)
        logging.info("Found {} deposits to validate".format(len(subdirs)))
        for d in subdirs:
            logging.debug("Validating {}".format(d))
            validate_dans_bag_in_deposit(os.path.join(path, d), package_type, level, service_baseurl, args.accept_json,
                                         dry_run)


if __name__ == '__main__':
    main()
