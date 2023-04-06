import argparse
from datastation.old.ingest_flow import unblock_target
from datastation.old.config import init


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Unblock a target allowing updates to be ingested')
    parser.add_argument('target', metavar='<target>', help='The target (a DOI or sword token) to unblock')
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                        help='Only print command to be sent to server, but do not actually send it')

    args = parser.parse_args()
    service_baseurl = config['ingest_flow']['service_baseurl']

    unblock_target(service_baseurl, args.target, is_dry_run=args.dry_run)


if __name__ == '__main__':
    main()
