import argparse
import os
from datetime import datetime

from datastation.common.batch_processing import BatchProcessor, get_pids
from datastation.common.config import init
from datastation.common.csv_report import CsvReport
from datastation.dataverse.dataverse_client import DataverseClient


def delete_dataset_drafts(args, dataverse_client: DataverseClient, batch_processor: BatchProcessor):
    pids = get_pids(args.pid_or_pid_file)
    headers = ["DOI", "Modified", "Change"]
    with CsvReport(os.path.expanduser(args.report_file), headers) as csv_report:
        batch_processor.process_pids(pids,
                                     lambda pid: delete_dataset_draft(pid,
                                                                      dataset_api=dataverse_client.dataset(pid),
                                                                      csv_report=csv_report))


def delete_dataset_draft(pid, dataset_api, csv_report):
    action = "None"
    if dataset_api.is_draft():
        print("Deleting dataset draft {}".format(pid))
        dataset_api.delete_draft()
        action = "Deleted"
    else:
        print("Dataset {} is not a draft".format(pid))
    csv_report.write({'DOI': pid, 'Modified': datetime.now(), 'Change': action})


def main():
    config = init()

    parser = argparse.ArgumentParser(description='Deletes one or more dataset drafts')
    parser.add_argument('pid_or_pid_file', help='The pid or file with pids of the datasets to delete')
    parser.add_argument('--delay', default=2.0, help="Delay between actions in seconds", dest='delay')
    parser.add_argument('--report-file', default='-', help="The report file, or - for stdout",
                        dest='report_file')
    args = parser.parse_args()

    dataverse_client = DataverseClient(config['dataverse'])
    batch_processor = BatchProcessor(delay=args.delay)

    delete_dataset_drafts(args, dataverse_client, batch_processor)
