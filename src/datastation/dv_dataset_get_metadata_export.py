import argparse

from datastation.common.batch_processing import BatchProcessor, get_pids
from datastation.common.config import init
from datastation.dataverse.dataverse_client import DataverseClient


def get_metadata_export(args, pid, dataverse):
    result = dataverse.dataset(pid).get_metadata_export(dry_run=args.dry_run, exporter=args.exporter)
    if args.output_dir:
        with open(f'{args.output_dir}/{pid}.{args.exorter}', 'w') as f:
            f.write(result)
    else:
        print(result)


def main():
    config = init()
    dataverse = DataverseClient(config['dataverse'])

    parser = argparse.ArgumentParser(description='Get metadata export for a dataset.')
    parser.add_argument('pid_or_pids_file',
                        help='The pid of the dataset to get the metadata export for, or a file with a list of pids')
    parser.add_argument('-d', '--dry-run', action='store_true', help="Do not actually get the metadata export")
    parser.add_argument('-w', '--wait-between-items', default=2.0, help="Number of seconds to wait between items",
                        dest='wait')
    parser.add_argument('-e', '--exporter', default='dataverse_json',
                        help="The exporter to use", dest='exporter')
    parser.add_argument('--fail-fast', action='store_true', help="Fail on the first error")
    parser.add_argument('-o', '--output-dir', help="The output directory where the exported metadata files will be "
                                                   "stored. If not provided, the files will be dumped to stdout",
                        dest='output_dir')

    args = parser.parse_args()
    batch_processor = BatchProcessor(wait=args.wait, fail_on_first_error=args.fail_fast)
    pids = get_pids(args.pid_or_pids_file)
    batch_processor.process_pids(pids,
                                 callback=lambda pid: get_metadata_export(args, pid, dataverse))
