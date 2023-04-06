import argparse
import logging
import os.path
import shutil

from datastation.config import init
from datastation.ingest_flow import set_permissions, is_subpath_of, is_dir_in_inbox


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Copy a batch to an ingest area')
    parser.add_argument('source', metavar='<source>', help='Source batch to copy')
    parser.add_argument('dest', metavar='<dest>', help='Destination to copy to. If the destination does not exist it is'
                                                       ' created and the contents of the batch is copied to it.')
    args = parser.parse_args()

    src = args.source
    batch_name = os.path.basename(src)
    dest = args.dest

    if os.path.isdir(dest):
        dest = os.path.join(dest, batch_name)

    dir_mode = int(config['ingest_flow']['deposits_mode']['directory'], 8)
    file_mode = int(config['ingest_flow']['deposits_mode']['file'], 8)
    deposits_group = config['ingest_flow']['deposits_group']
    ingest_areas = config['ingest_flow']['ingest_areas']
    inboxes = list(map(lambda a: a['inbox'], ingest_areas.values()))
    logging.debug("Found inboxes {}".format(", ".join(inboxes)))
    if is_dir_in_inbox(dest, inboxes):
        logging.debug("Copying from {} to {}".format(args.source, dest))
        shutil.copytree(src=args.source, dst=dest)
        logging.debug("Setting permissions and group...")
        set_permissions(dest, dir_mode, file_mode, deposits_group)
        logging.info("Done")
    else:
        print("Destination {} is not located in a configured ingest area inbox (one of {})".format(dest,
                                                                                                   ", ".join(inboxes)))
        exit(1)
