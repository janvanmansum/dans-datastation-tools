import argparse

from datastation.common.config import init


def main():
    config = init()

    parser = argparse.ArgumentParser(description='Commands to control the ingest flow')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    parser_start_migration = subparsers.add_parser('start-migration', help='Start migration of deposit or batch of deposits')
    parser_start_migration.add_argument('deposit_path', metavar='<batch-or-deposit>', help='Directory containing one deposit or a batch of deposits')
    parser_start_migration.add_argument('-s', '--single', dest="single_deposit", action="store_true",
                        help="<batch-or-deposit> refers to a single deposit")
    parser_start_migration.add_argument('-c', '--continue', dest='continue_previous', action='store_true',
                        help="continue previously stopped batch (i.e. allow output directory to be non-empty)")
    parser_start_migration.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                        help='Only print command to be sent to server, but do not actually send it')

    parser_start_ingest = subparsers.add_parser('start-ingest', help='Start ingest of deposit or batch of deposits')
    parser_start_ingest.add_argument('deposit_path', metavar='<batch-or-deposit>', help='Directory containing one deposit or a batch of deposits')
    parser_start_ingest.add_argument('-s', '--single', dest="single_deposit", action="store_true",
                        help="<batch-or-deposit> refers to a single deposit")
    parser_start_ingest.add_argument('-c', '--continue', dest='continue_previous', action='store_true',
                        help="continue previously stopped batch (i.e. allow output directory to be non-empty)")
    parser_start_ingest.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                        help='Only print command to be sent to server, but do not actually send it')

    args = parser.parse_args()



