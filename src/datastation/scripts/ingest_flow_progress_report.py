import argparse
import logging

from datastation.ingest_flow import progress_report
from datastation.config import init


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Print progress report for a batch. The progress report consists of a timestamp,'
                                     ' and the numbers of deposits still to do, processed, rejected and failed. If a directory is passed that is'
                                     ' not in one of the configured ingest areas, an error is returned.')
    parser.add_argument('deposits_batch', metavar='<deposits-batch>', help='Path to the batch of deposits to print the progress report for')

    args = parser.parse_args()
    progress_report(args.deposits_batch, config['ingest_flow']['ingest_areas'].values())



if __name__ == '__main__':
    main()
