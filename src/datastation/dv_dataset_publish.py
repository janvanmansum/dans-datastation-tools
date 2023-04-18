import argparse
import json
from datetime import datetime

from datastation.common.batch_processing import BatchProcessorWithReport, get_pids
from datastation.common.config import init
from datastation.dataverse.dataverse_client import DataverseClient


def publish_datasets(args, dataverse_client: DataverseClient):
    pids = get_pids(args.pid_or_pid_file)
    batch_processor = BatchProcessorWithReport(report_file=args.report_file, wait=args.wait,
                                               fail_on_first_error=args.fail_fast,
                                               headers=['DOI', 'Modified', 'Change', 'Messages'])
    batch_processor.process_pids(pids,
                                 lambda pid, csv_report: publish(pid, dataverse_client,
                                                                 update_type=args.update_type,
                                                                 csv_report=csv_report,
                                                                 dry_run=args.dry_run))


def publish(pid, dataverse_client: DataverseClient, update_type, csv_report, dry_run: bool = False):
    dataset_api = dataverse_client.dataset(pid)
    message = ''
    if dataset_api.is_draft():
        print("Dataset {} is a draft. Publishing it.".format(pid))
        r = dataset_api.publish(update_type=update_type, dry_run=dry_run)
        action = "Published"
        if r is not None:
            message = json.dumps(r['data'])
    else:
        print(f"Dataset {pid} is not in draft state. Skipping it.")
        action = "None"
    csv_report.write({'DOI': pid, 'Modified': datetime.now(), 'Change': action, 'Messages': message})


def main():
    config = init()
    dataverse = DataverseClient(config['dataverse'])
    update_types = ['major', 'minor', 'updatecurrent']

    parser = argparse.ArgumentParser(description='Publish a dataset.')
    parser.add_argument('pid_or_pid_file',
                        help='the persistent identifier of the dataset or a file containing a list of '
                             'persistent identifiers.')
    parser.add_argument('-u', '--update-type', dest='update_type',
                        help='whether to create a major, version or update the '
                             'current version (default: major)', choices=update_types, default='major')
    parser.add_argument('-r', '--report-file', default='-', help="The report file, or - for stdout",
                        dest='report_file')
    parser.add_argument('-w', '--wait-between-items', default=2.0,
                        help="Number of seconds to wait between processing items",
                        dest='wait')
    parser.add_argument('-f', '--fail-fast', dest='fail_fast', action='store_true', help='fail on first error ')
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true', help='do not actually publish the '
                                                                                     'dataset. (default: false)')

    args = parser.parse_args()
    publish_datasets(args, dataverse)
