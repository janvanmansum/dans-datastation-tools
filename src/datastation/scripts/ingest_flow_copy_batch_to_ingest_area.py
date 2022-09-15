import argparse
import os.path
import shutil

from datastation.config import init
from datastation.ingest_flow import set_permissions, is_subpath_of


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

    if next(filter(lambda p: is_subpath_of(dest, p), ingest_areas), None) is None:
        print("Destination {} is not located in a configured ingest area".format(dest))
        return 1

    shutil.copytree(src=args.source, dst=dest)
    set_permissions(dest, dir_mode, file_mode, deposits_group)

    return 0
