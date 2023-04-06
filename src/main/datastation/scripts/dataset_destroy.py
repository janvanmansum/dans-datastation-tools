import argparse
import logging

from datastation.config import init
from datastation.dv_api import destroy_dataset


def main():
    config = init()
    parser = argparse.ArgumentParser(
        description='Destroy a published dataset. Requires dataverse.safety_latch = OFF + superadmin permissions in '
                    'Dataverse. Bulk processing NOT SUPPORTED.')
    parser.add_argument('pid', help='The PID of the dataset to destroy')
    args = parser.parse_args()

    safety_latch = True  # If no safety_latch is found, assume it is ON
    if 'safety_latch' in config['dataverse']:
        safety_latch = config['dataverse']['safety_latch']
    pid = args.pid
    server_url = config['dataverse']['server_url']
    api_token = config['dataverse']['api_token']
    if safety_latch:
        print("safety_latch is ON. Not performing destroy.")
    else:
        logging.info("safety_latch is OFF. Destroying {}".format(pid))
        destroy_dataset(server_url, api_token, pid)


if __name__ == '__main__':
    main()
