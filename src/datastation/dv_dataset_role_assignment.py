import argparse
from datetime import datetime

import rich

from datastation.common.batch_processing import get_pids, BatchProcessor, BatchProcessorWithReport
from datastation.common.config import init
from datastation.dataverse.dataset_api import DatasetApi
from datastation.dataverse.dataverse_client import DataverseClient


def add_role_assignments(args, dataverse_client: DataverseClient, batch_processor: BatchProcessor):
    pids = get_pids(args.pid_or_pid_file)
    batch_processor.process_pids(pids,
                                 lambda pid, csv_report: add_role_assignment(args.role_assignment,
                                                                             dataset_api=dataverse_client.dataset(pid),
                                                                             csv_report=csv_report))


def add_role_assignment(role_assignment, dataset_api: DatasetApi, csv_report):
    assignee = role_assignment.split('=')[0]
    role = role_assignment.split('=')[1]
    action = "None"
    if in_current_assignments(assignee, role, dataset_api):
        print("{} is already {} for dataset {}".format(assignee, role, dataset_api.get_pid()))
    else:
        print(
            "Adding {} as {} for dataset {}".format(assignee, role, dataset_api.get_pid()))
        dataset_api.add_role_assignment(assignee, role)
        action = "Added"
    csv_report.write(
        {'DOI': dataset_api.get_pid(), 'Modified': datetime.now(), 'Assignee': assignee, 'Role': role,
         'Change': action})


def in_current_assignments(assignee, role, dataset_api: DatasetApi):
    current_assignments = dataset_api.get_role_assignments()
    found = False
    for current_assignment in current_assignments:
        if current_assignment.get('assignee') == assignee and current_assignment.get(
                '_roleAlias') == role:
            found = True
            break
    return found


def list_role_assignments(args, dataverse_client):
    r = dataverse_client.dataset(args.pid).get_role_assignments()
    if r is not None:
        rich.print_json(data=r)


def remove_role_assignments(args, dataverse_client: DataverseClient, batch_processor: BatchProcessor):
    pids = get_pids(args.pid_or_pid_file)
    batch_processor.process_pids(pids,
                                 lambda pid, csv_report: remove_role_assignment(args.role_assignment,
                                                                                dataset_api=dataverse_client.dataset(
                                                                                    pid),
                                                                                csv_report=csv_report))


def remove_role_assignment(role_assignment, dataset_api: DatasetApi, csv_report):
    assignee = role_assignment.split('=')[0]
    role = role_assignment.split('=')[1]
    action = "None"
    if in_current_assignments(assignee, role, dataset_api):
        print("Removing {} as {} for dataset {}".format(assignee, role, dataset_api.get_pid()))
        all_assignments = dataset_api.get_role_assignments()
        for assignment in all_assignments:
            if assignment.get('assignee') == assignee and assignment.get('_roleAlias') == role:
                dataset_api.remove_role_assignment(assignment.get('id'))
                action = "Removed"
                break
    else:
        print("{} is not {} for dataset {}".format(assignee, role, dataset_api.get_pid()))
    csv_report.write(
        {'DOI': dataset_api.get_pid(), 'Modified': datetime.now(), 'Assignee': assignee, 'Role': role,
         'Change': action})


def main():
    config = init()
    dataverse_client = DataverseClient(config['dataverse'])
    batch_processor = BatchProcessorWithReport(headers=['DOI', 'Modified', 'Assignee', 'Role', 'Change'])

    parser = argparse.ArgumentParser(description='manage role assignments on one or more datasets')
    parser.add_argument('-d', '--dry-run', dest='dry_run', help="only logs the actions, nothing is executed",
                        action='store_true')
    parser.add_argument('-s', '--sleep', dest='sleep', help="sleep time between requests", type=int, default=0)
    parser.add_argument('-f', '--fail-fast', dest='fail_fast', help="stop on first error", action='store_true')
    parser.add_argument('-r', '--report', required=True, dest='report_file',
                        help='destination of the output report file, "-" sends it to stdout')

    subparsers = parser.add_subparsers(help='subcommands', dest='subcommand')

    # Add role assignment
    parser_add = subparsers.add_parser('add', help='add role assignment to specified dataset(s)')
    parser_add.add_argument('-a', '--role-assignment', dest='role_assignment',
                            help='role assignee and alias (example: @dataverseAdmin=contributor)')
    parser_add.add_argument('pid_or_pid_file', help='the dataset pid or the input file with the dataset pids')
    parser_add.set_defaults(func=lambda _: add_role_assignments(_, dataverse_client, batch_processor))

    # Remove role assignment
    parser_remove = subparsers.add_parser('remove', help='Remove role assignment from specified dataset(s)')
    parser_remove.add_argument('-a', '--role-assignment',
                               dest='role_assignment',
                               help='Role assignee and alias (example: @dataverseAdmin=contributor)')
    parser_remove.add_argument('-r', '--report', required=True, dest='report_file',
                               help='Destination of the output report file, "-" sends it to stdout')
    parser_remove.add_argument('pid_or_pid_file', help='The dataset pid or the input file with the dataset pids')
    parser_remove.set_defaults(func=lambda _: remove_role_assignments(_, dataverse_client, batch_processor))

    # List role assignments
    parser_list = subparsers.add_parser('list',
                                        help='list role assignments for specified dataset (only one pid allowed)')
    parser_list.add_argument('pid', help='the dataset pid')
    parser_list.set_defaults(func=lambda _: list_role_assignments(_, dataverse_client))

    args = parser.parse_args()

    # Prepare the batch processor and the dataverse client
    dataverse_client.set_dry_run(args.dry_run)
    batch_processor.set_delay(args.sleep)
    batch_processor.set_fail_on_first_error(args.fail_fast)
    batch_processor.set_report_file(args.report_file)

    # Execute the command
    args.func(args)
