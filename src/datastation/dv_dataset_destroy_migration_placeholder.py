import argparse

from datastation.common.batch_processing import BatchProcessor, get_pids, BatchProcessorWithReport
from datastation.common.config import init
from datastation.dataverse.dataverse_client import DataverseClient
from datastation.dataverse.destroy_placeholder_dataset import destroy_placeholder_dataset


def main():
    config = init()
    dataverse = DataverseClient(config['dataverse'])

    parser = argparse.ArgumentParser(
        description='Destroys a dataset that is a placeholder for a dataset that has not yet been migrated. In order '
                    'to validate that the dataset is a placeholder, the dataset must be published. Furthermore, '
                    'the description of the dataset must match the pattern configured in '
                    'migration_placeholders.description_text_pattern. Note, that the safety latch must also be OFF.')
    parser.add_argument('pid_or_pids_file', help='The pid of the dataset to destroy, or a file with a list of pids')
    parser.add_argument('-d', '--dry-run', action='store_true', help="Do not actually destroy the dataset")
    parser.add_argument('-w', '--wait-between-items', default=2.0, help="Delay between actions in seconds", dest='wait')
    parser.add_argument('-r', '--report-file', default='-', help="The report file, or - for stdout", dest='report_file')
    args = parser.parse_args()

    batch_processor = BatchProcessorWithReport(delay=args.wait, report_file=args.report_file,
                                               headers=['PID', 'Destroyed', 'Messages'])
    dataverse.set_dry_run(args.dry_run)
    pids = get_pids(args.pid_or_pids_file)
    description_text_pattern = config['migration_placeholders']['description_text_pattern']
    batch_processor.process_pids(pids,
                                 callback=lambda pid, csv_report: destroy_placeholder_dataset(dataverse.dataset(pid),
                                                                                              description_text_pattern,
                                                                                              csv_report))
