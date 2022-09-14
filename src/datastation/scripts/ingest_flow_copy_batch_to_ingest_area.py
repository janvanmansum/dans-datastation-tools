import argparse
import shutil

from datastation.config import init


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Copy a batch to an ingest area')
    parser.add_argument('source', metavar='<source>', help='Source batch to copy')
    parser.add_argument('dest', metavar='<dest>', help='Destination to copy to. If the destination does not exist it is'
                                                       ' created and the contents of the batch is copied to it.')
    args = parser.parse_args()

    shutil.copytree(src=args.source, dst=args.dest)

    return 0
