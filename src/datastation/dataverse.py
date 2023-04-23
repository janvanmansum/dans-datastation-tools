import argparse

from datastation.common.config import init


def add_dataset_args(parser):
    parser.add_argument('pid', help='the persistent identifier of the dataset.')
    parser.add_argument('--version', help='the version of the dataset.', default=':latest')
    subparsers = parser.add_subparsers(help='subcommands', dest='subcommand')
    publish_parser = subparsers.add_parser('publish', help='publish a dataset')
    group = publish_parser.add_mutually_exclusive_group()
    group.add_argument('-M', '--major', help='publish a major version', action='store_true')
    group.add_argument('-m', '--minor', help='publish a minor version', action='store_true')
    group.add_argument('-u', '--update-current', help='overwrite the current version', action='store_true')


def main():
    config = init()

    parser = argparse.ArgumentParser('Operations on Dataverse')
    subparsers = parser.add_subparsers(help='subcommands', dest='subcommand')

    parser_dataset = subparsers.add_parser('dataset', help='Operations on a dataset')
    add_dataset_args(parser_dataset)
