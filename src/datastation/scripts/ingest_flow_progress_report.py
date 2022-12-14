import argparse
from datastation.ingest_flow import start_import
from datastation.config import init


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Print progress report for a batch')
    parser.add_argument('deposits_batch', metavar='<deposits-batch>', help='Path to the batch of deposits to print the progress report for')

    args = parser.parse_args()



if __name__ == '__main__':
    main()
