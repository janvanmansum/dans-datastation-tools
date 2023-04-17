import argparse
from datetime import datetime

from datastation.common.batch_processing import BatchProcessor, get_pids, BatchProcessorWithReport
from datastation.common.config import init
from datastation.dataverse.dataverse_client import DataverseClient


def delete_dataset_drafts(args, dataverse_client: DataverseClient, batch_processor: BatchProcessor):
    pids = get_pids(args.pid_or_pid_file)
    batch_processor.process_pids(pids,
                                 lambda pid, csv_report: delete_dataset_draft(pid,
                                                                              dataset_api=dataverse_client.dataset(pid),
                                                                              csv_report=csv_report,
                                                                              dry_run=args.dry_run))


def delete_dataset_draft(pid, dataset_api, csv_report, dry_run: bool):
    action = "None"
    if dataset_api.is_draft():
        print("Deleting dataset draft {}".format(pid))
        dataset_api.delete_draft(dry_run=dry_run)
        action = "Deleted"
    else:
        print("Dataset {} is not a draft".format(pid))
    csv_report.write({'DOI': pid, 'Modified': datetime.now(), 'Change': action})


def main():
    config = init()

    parser = argparse.ArgumentParser(description='Deletes one or more dataset drafts')
    parser.add_argument('pid_or_pid_file', help='The pid or file with pids of the datasets to delete')
    parser.add_argument('--wait-between-items', default=2.0, help="Number of seconds to wait between processing items",
                        dest='wait')
    parser.add_argument('--report-file', default='-', help="The report file, or - for stdout",
                        dest='report_file')
    parser.add_argument('-d', '--dry-run', action='store_true', help="Do not actually delete the datasets")
    args = parser.parse_args()

    dataverse_client = DataverseClient(config['dataverse'])
    batch_processor = BatchProcessorWithReport(wait=args.wait, report_file=args.report_file)
    delete_dataset_drafts(args, dataverse_client, batch_processor)
