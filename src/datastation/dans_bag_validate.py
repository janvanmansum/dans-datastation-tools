import argparse
import sys

from datastation.common.result_writer import CsvResultWriter, JsonResultWriter, YamlResultWriter
from src.datastation.common.config import init
from src.datastation.dans_bag.dans_bag_validator import DansBagValidator


class DansBagValidateCommand:

    def __init__(self, config, path, information_package_type, accept_type, output_format, dry_run=False):
        self.config = config
        self.path = path
        self.information_package_type = information_package_type
        self.accept_type = accept_type
        self.dry_run = dry_run
        if output_format == 'csv':
            self.result_writer = CsvResultWriter(headers=['Bag location', 'Information package type', 'Is compliant',
                                                          'Name', 'Profile version', 'Rule violations'],
                                                 out_stream=sys.stdout)
        elif output_format == 'yaml':
            self.result_writer = YamlResultWriter(out_stream=sys.stdout)
        else:
            self.result_writer = JsonResultWriter(out_stream=sys.stdout)

    def run(self):
        validator = DansBagValidator(self.config['dans_bag_validator'], accept_type=self.accept_type,
                                     dry_run=self.dry_run)
        validator.validate(self.path, self.information_package_type, self.result_writer)


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
                        help='Output format, one of: csv, json, yaml (default: json)')
    parser.add_argument('-a', '--accept', dest='accept', default='application/json',
                        help='Accept header to send to server. Note that the server only supports application/json and'
                             'text/plain, the latter will return YAML. This option is only useful for debugging '
                             'purposes. (default: application/json)')

    args = parser.parse_args()
    DansBagValidateCommand(config, args.path, args.info_package_type, args.accept, args.format, args.dry_run).run()
