import argparse
from datastation.ingest_flow import start_import
from datastation.config import init


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Start migration of deposit or batch of deposits')
    parser.add_argument('deposit_path', metavar='<batch-or-deposit>', help='The input file with the dataset pids')
    parser.add_argument('-s', '--single', dest="single_deposit", action="store_true",
                        help="<batch-or-deposit> refers to a single deposit")
    parser.add_argument('-c', '--continue', dest='continue_previous', action='store_true',
                        help="continue previously stopped batch (i.e. allow output directory to be non-empty)")
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                        help='Only print command to be sent to server, but do not actually send it')

    args = parser.parse_args()
    service_baseurl = config['ingest_flow']['service_baseurl']

    start_import(service_baseurl, args.deposit_path, not args.single_deposit, args.continue_previous, is_migration=True,
                 is_dry_run=args.dry_run)


if __name__ == '__main__':
    main()
