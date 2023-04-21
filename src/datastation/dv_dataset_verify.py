import argparse

import rich

from datastation.common.config import init
from datastation.common.utils import add_dry_run_arg
from datastation.verifydataset.verify_dataset import VerifyDatasetService


def main():
    config = init()
    verify_dataset_service = VerifyDatasetService(config['verify_dataset'])

    parser = argparse.ArgumentParser(description='Verify metadata of a dataset')
    parser.add_argument('pid_or_pid_file', help='The pid or file with pids of the datasets to verify')
    add_dry_run_arg(parser)

    args = parser.parse_args()
    r = verify_dataset_service.verify_dataset(args.pid_or_pid_file, dry_run=args.dry_run)
    rich.print_json(data=r)
