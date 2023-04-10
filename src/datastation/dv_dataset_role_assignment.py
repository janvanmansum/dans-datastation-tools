import argparse

import rich

from datastation.common.batch_processing import get_pids, BatchProcessor
from datastation.common.config import init

from datastation.dataverse.dataverse_client import DataverseClient


def add_role_assignment(args, dataverse_client: DataverseClient, batch_processor: BatchProcessor):
    pids = get_pids(args.pid_or_pid_file)
    batch_processor.process_pids(pids,
                                 lambda pid: dataverse_client.dataset(pid).add_role_assignment(args.role_assignment))
    # todo: handle case where assignment already exists


def list_role_assignments(args, dataverse_client):
    r = dataverse_client.dataset(args.pid).get_role_assignments()
    if r is not None:
        rich.print_json(data=r.json())


def main():
    config = init()
    dataverse_client = DataverseClient(config['dataverse'])
    batch_processor = BatchProcessor()

    parser = argparse.ArgumentParser(description='Manage role assignments on one or more datasets')
    parser.add_argument('-d', '--dry-run', dest='dry_run', help="only logs the actions, nothing is executed",
                        action='store_true')
    parser.add_argument('-s', '--sleep', dest='sleep', help="sleep time between requests", type=int, default=0)
    parser.add_argument('-f', '-fail-fast', dest='fail_fast', help="stop on first error", action='store_true')

    subparsers = parser.add_subparsers(help='sub-command help', dest='subcommand')

    # Add role assignment
    parser_add = subparsers.add_parser('add', help='Add role assignment to specified dataset(s)')
    parser_add.add_argument('-a', '--role-assignment', dest='role_assignment',
                            help='Role assignee and alias (example: @dataverseAdmin=contributor)')
    parser_add.add_argument('-r', '--report', required=True, dest='output_file',
                            help='Destination of the output report file, "-" sends it to stdout')
    parser_add.add_argument('pid_or_pid_file', help='The dataset pid or the input file with the dataset pids')
    parser_add.set_defaults(func=lambda _: add_role_assignment(_, dataverse_client))

    # Remove role assignment
    parser_remove = subparsers.add_parser('remove', help='Remove role assignment from specified dataset(s)')
    parser_remove.add_argument('-a', '--role-assignment',
                               help='Role assignee and alias (example: @dataverseAdmin=contributor)')
    parser_remove.add_argument('-r', '--report', required=True, dest='output_file',
                               help='Destination of the output report file, "-" sends it to stdout')
    parser_remove.add_argument('pid_or_pid_file', help='The dataset pid or the input file with the dataset pids')

    # List role assignments
    parser_list = subparsers.add_parser('list',
                                        help='List role assignments for specified dataset (only one pid allowed)')
    parser_list.add_argument('pid', help='The dataset pid')
    parser_list.set_defaults(func=lambda _: list_role_assignments(_, dataverse_client))

    args = parser.parse_args()
    dataverse_client.set_dry_run(args.dry_run)
    batch_processor.set_delay(args.sleep)
    batch_processor.set_fail_on_first_error(args.fail_fast)
    args.func(args)
