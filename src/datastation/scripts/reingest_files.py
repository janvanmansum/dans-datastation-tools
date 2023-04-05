import argparse
from datastation.dv_dataset import reingest_files
from datastation.config import init

def main():
    config = init()
    parser = argparse.ArgumentParser(description='Reingests tabular files from specified datasets.')

    # mutually exclusive group of doi or pids_file
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('doi', nargs='?', metavar='<doi>', help='A dataset pid')
    group.add_argument('-p', '--pids-file', dest="pids_file", help="a file with a list of dataset pid's to scan, separated by newlines")
    
    args = parser.parse_args()

    server_url = config['dataverse']['server_url']
    api_token = config['dataverse']['api_token']
    poll_interval_seconds = int(config['reingest_files']['poll_interval_seconds'])

    reingest_files(server_url, api_token, args.doi, args.pids_file, poll_interval_seconds)


if __name__ == '__main__':
    main()
