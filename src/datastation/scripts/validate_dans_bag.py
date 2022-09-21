import argparse
import json
import logging
import os

import requests

from datastation.config import init
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def validate_dans_bag(path, package_type, level, validator_url, is_dry_run):
    parts = {
        'command': ('command',
                    bytes(json.dumps({
                        'bagLocation': os.path.abspath(path),
                        'packageType': package_type,
                        'level': level
                    }), "utf-8"), 'application/json')
    }
    session = requests.Session()
    if is_dry_run:
        logging.info("Only printing command, not sending it...")
        print(parts)
    else:
        r = session.post('{}/validate'.format(validator_url), files=parts,
                         headers={'Content-Type': 'multipart/form-data'})
        print('Server responded: %s' % r.text)

    return 0


def get_subdirs(dir):
    return list(filter(lambda d: os.path.isdir(os.path.join(dir, d)), os.listdir(dir)))


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

    args = parser.parse_args()
    service_baseurl = config['dans_bag_validator']['service_baseurl']
    package_type = "MIGRATION" if args.is_migration else "DEPOSIT"
    level = "WITH-DATA-STATION-CONTEXT" if args.in_context else "STAND-ALONE"
    dry_run = args.dry_run

    path = args.path

    if os.path.exists("{}/bagit.txt".format(path)):
        logging.info("Found one bag at {}".format(path))
        validate_dans_bag(path, package_type, level, service_baseurl, dry_run)
    elif os.path.exists("{}/deposit.properties".format(path)):
        logging.info("Found a deposit at {}".format(path))
        subdirs = get_subdirs(path)
        if len(subdirs) == 1:
            validate_dans_bag(subdirs[0], package_type, level, service_baseurl, dry_run)
        else:
            print("ERROR: deposit found with {} subdirectories. There should be exactly one".format(len(subdirs)))
    else:
        logging.info("Not a bag or a deposit, assuming batch of deposits")
        subdirs = get_subdirs(path)
        for d in subdirs:
            validate_dans_bag(d, package_type, level, service_baseurl, dry_run)


if __name__ == '__main__':
    main()
