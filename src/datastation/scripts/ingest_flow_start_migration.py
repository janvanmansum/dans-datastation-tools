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

    args = parser.parse_args()

    start_import(args.deposit_path, args.continue_previous, is_migration=True)


if __name__ == '__main__':
    main()
