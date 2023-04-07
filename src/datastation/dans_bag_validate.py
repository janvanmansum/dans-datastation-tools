import argparse

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
    parser.add_argument('-o', '--out-file', dest='out_file',
                        required=True,
                        help='Output file to save results to. If the file name ends in .csv the output is saved as CSV,'
                             'if .json as JSON and otherwise as Yaml')

    args = parser.parse_args()
    validator = DansBagValidator(config['dans_bag_validator'])
    validator.validate(args.path, args.info_package_type, args.dry_run, args.out_file)
