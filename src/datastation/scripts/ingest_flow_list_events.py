import argparse
from datastation.ingest_flow import start_import, list_events
from datastation.config import init


def main():
    config = init()
    parser = argparse.ArgumentParser(description='List the events per deposit')
    parser.add_argument('-s', '--source',
                        dest='source',
                        metavar='<source>',
                        help='only events for this source (i.e. batch or auto-ingest)')
    parser.add_argument('-d', '--deposit',
                        metavar='<uuid>',
                        dest='deposit_id',
                        help='only events for this deposit')
    args = parser.parse_args()

    params = {}
    if args.source is not None:
        params['source'] = args.source
    if args.deposit_id is not None:
        params['depositId'] = args.deposit_id

    service_url = config['ingest_flow']['service_baseurl']
    list_events(service_url, params)


if __name__ == '__main__':
    main()
