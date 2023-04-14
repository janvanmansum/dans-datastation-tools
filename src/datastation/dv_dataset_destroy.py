import argparse
from datetime import datetime

from datastation.common.batch_processing import BatchProcessor, get_pids, BatchProcessorWithReport
from datastation.common.config import init
from datastation.dataverse.dataverse_client import DataverseClient


def destroy_datasets(args, dataverse_client: DataverseClient, batch_processor: BatchProcessor):
    pids = get_pids(args.pid_or_pid_file)
    batch_processor.process_pids(pids, lambda pid, csv_report: destroy_dataset(pid,
                                                                               dataset_api=dataverse_client.dataset(
                                                                                   pid),
                                                                               csv_report=csv_report))


def destroy_dataset(pid, dataset_api, csv_report):
    print("Destroying dataset {}".format(pid))
    dataset_api.destroy()
    action = "Destroyed"
    csv_report.write({'DOI': pid, 'Modified': datetime.now(), 'Change': action})


def main():
    config = init()

    parser = argparse.ArgumentParser(
        description='Deletes one or more, potentially published, datasets. Requires an API token with superuser '
                    'privileges. Furthermore, the dataverse.safety_latch must be set to OFF.')
    parser.add_argument('pid_or_pid_file', help='The pid or file with pids of the datasets to destroy')
    parser.add_argument('--delay', default=2.0, help="Delay between actions in seconds", dest='delay')
    parser.add_argument('-r', '--report-file', default='-', help="The report file, or - for stdout", dest='report_file')
    parser.add_argument('--dry-run', action='store_true', help="Do not actually delete the datasets")
    args = parser.parse_args()

    dataverse_client = DataverseClient(config['dataverse'], dry_run=args.dry_run)
    batch_processor = BatchProcessorWithReport(delay=args.delay, report_file=args.report_file)

    destroy_datasets(args, dataverse_client, batch_processor)
