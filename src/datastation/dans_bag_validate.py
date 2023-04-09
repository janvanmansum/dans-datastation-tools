import argparse
import sys

from datastation.common.result_writer import CsvResultWriter, JsonResultWriter, YamlResultWriter
from src.datastation.common.config import init
from src.datastation.dans_bag.dans_bag_validator import DansBagValidator


def main():
    config = init()

    parser = argparse.ArgumentParser(
        description='Validate one or more bags to see if they comply with the DANS BagIt Profile v1')
    parser.add_argument('path', metavar='<batch-or-deposit-or-bag>',
                        help='Directory containing a bag, a deposit or a batch of deposits')
    parser.add_argument('-t', '--information-package-type', dest='info_package_type',
                        help='Which information package type to validate this bag as',
                        choices=['DEPOSIT', 'MIGRATION'],
                        default='MIGRATION')
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                        help='Only print command to be sent to server, but do not actually send it')
    parser.add_argument('-f', '--format', dest='format',
                        required=True,
                        help='Output format, one of: csv, json, yaml (default: json)')

    args = parser.parse_args()
    validator = DansBagValidator(config['dans_bag_validator'], dry_run=args.dry_run)
    if args.format == 'csv':
        result_writer = CsvResultWriter(headers=['DEPOSIT', 'BAG', 'COMPLIANT', 'RULE VIOLATIONS'],
                                        out_stream=sys.stdout)
    elif args.format == 'yaml':
        result_writer = YamlResultWriter(out_stream=sys.stdout)
    else:
        result_writer = JsonResultWriter(out_stream=sys.stdout)

    validator.validate(args.path, args.info_package_type, result_writer)
