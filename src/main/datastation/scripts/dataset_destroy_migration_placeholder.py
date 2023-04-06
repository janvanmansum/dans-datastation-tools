import argparse
import logging

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.ds_pidsfile import load_pids
from datastation.dv_api import get_dataset_metadata, destroy_dataset
from re import match


def description_object_matches(description_text_pattern):
    def matches(description):
        value = description['dsDescriptionValue']['value']
        return match(description_text_pattern, value)

    return matches


def has_directoryLabel_different_from(file_metadata, dir_label):
    return 'directoryLabel' not in file_metadata or file_metadata['directoryLabel'] != dir_label


def destroy_placeholder_dataset(server_url, api_token, pid, description_text_pattern, dry_run):
    blocker = False
    try:
        dataset_metadata = get_dataset_metadata(server_url, api_token, pid)
        dsDescription = next(
            filter(lambda m: m['typeName'] == 'dsDescription', dataset_metadata['metadataBlocks']['citation']['fields']))
        descriptions = dsDescription['value']

        if len(list(filter(description_object_matches(description_text_pattern), descriptions))) == 0:
            blocker = True
            logging.warning("No description found matching pattern '{}'".format(description_text_pattern))
        else:
            logging.debug("Description with text pattern found: OK")

        files = dataset_metadata['files']

        if len(files) > 4:
            blocker = True
            logging.warning("More than 4 files found: {}".format(files))
        else:
            logging.debug("Found {} files <= 4: OK".format(len(files)))

        non_easy_migration_files = list(filter(lambda m: has_directoryLabel_different_from(m, 'easy-migration'), files))

        if len(non_easy_migration_files) > 0:
            blocker = True
            logging.warning("Files other than 'easy-migration' found: {}".format(non_easy_migration_files))
        else:
            logging.debug("Only found easy-migration files: OK")
    except Exception as e:
        blocker = True
        logging.warning("Could not perform checks on dataset {}".format(pid), exc_info=e)


    if blocker:
        logging.warning("BLOCKERS FOUND, NOT PERFORMING DESTROY FOR {}".format(pid))
    elif dry_run:
        logging.info("--dry-run option specified. Not performing destroy for {}".format(pid))
    else:
        logging.info("Destroying {}".format(pid))
        destroy_dataset(server_url, api_token, pid)


def main():
    config = init()
    server_url = config['dataverse']['server_url']
    api_token = config['dataverse']['api_token']
    description_text_pattern = config['migration_placeholders']['description_text_pattern']

    parser = argparse.ArgumentParser(
        description='Destroy metadata-only placeholders for datasets that have not been migrated yet')
    pid_or_file = parser.add_mutually_exclusive_group()
    pid_or_file.add_argument('-p', '--pid', dest='pid', help='Pid of a single placeholder dataset to destroy')
    pid_or_file.add_argument('-d', '--datasets', dest='pid_file', help='The input file with the dataset pids')
    parser.add_argument('--dry-run', dest='dry_run', help="only logs the actions, nothing is executed",
                        action='store_true')

    args = parser.parse_args()

    if args.pid is not None:
        destroy_placeholder_dataset(server_url, api_token, args.pid, description_text_pattern, args.dry_run)
    if args.pid_file is not None:
        pids = load_pids(args.pid_file)
        batch_process(pids,
                      lambda pid: destroy_placeholder_dataset(server_url, api_token, pid, description_text_pattern,
                                                              args.dry_run))


if __name__ == '__main__':
    main()
