import argparse
import requests
import json

from datastation.config import init


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Verify metadata of a dataset')
    parser.add_argument(dest='doi', help='The doi of the dataset to verify, e.g. "doi:10.5072/DAR/RGICM5"')
    args = parser.parse_args()

    server_url = config['verify_dataset']['url']

    response = requests.post(f'{server_url}/verify',
                             data='{ "datasetPid": "' + args.doi + '" }',
                             headers={'Content-Type': 'application/json'})
    print(f"response code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


if __name__ == '__main__':
    main()
