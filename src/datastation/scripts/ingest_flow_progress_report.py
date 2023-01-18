import argparse
import logging

from datastation.ingest_flow import progress_report
from datastation.config import init


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Print progress report for a batch')
    parser.add_argument('deposits_batch', metavar='<deposits-batch>', help='Path to the batch of deposits to print the progress report for')

    args = parser.parse_args()
    progress_report(args.deposits_batch, config['ingest_flow']['ingest_areas'].values())



if __name__ == '__main__':
    main()
