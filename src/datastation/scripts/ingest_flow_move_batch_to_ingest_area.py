import argparse
import os.path
import shutil

from datastation.config import init


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Move a batch to an ingest area')
    parser.add_argument('source', metavar='<source>', help='Source batch to move')
    parser.add_argument('dest', metavar='<dest>', help='Destination to move to. If the destination does not exist it is'
                                                       ' created and the contents of the batch is copied to it.')
    args = parser.parse_args()

    src = args.source
    batch_name = os.path.basename(src)
    dest = args.dest

    if os.path.isdir(dest):
        dest = os.path.join(dest, batch_name)

    shutil.move(src=args.source, dst=dest)

    return 0
