import argparse


from datastation.common.config import init
from datastation.common.utils import add_dry_run_arg
from datastation.dataverse.dataverse_client import DataverseClient
from datastation.dataverse.permissions_collect import PermissionsCollect


def main():
    config = init()

    parser = argparse.ArgumentParser(description='Collect the permissions overview for the dataverses')
    parser.add_argument('-o', '--output-file', dest='output_file', default='-',
                        help='the file to write the output to or - for stdout')
    parser.add_argument('-f', '--format', dest='format',
                        help='Output format, one of: csv, json (default: json)')

    add_dry_run_arg(parser)
    args = parser.parse_args()

    dataverse_client = DataverseClient(config['dataverse'])
    collector = PermissionsCollect(dataverse_client, args.output_file, args.format, args.dry_run)
    collector.collect_permissions_info()

if __name__ == '__main__':
    main()