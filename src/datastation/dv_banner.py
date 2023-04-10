import argparse

import rich

from datastation.common.config import init
from datastation.dataverse.dataverse_client import DataverseClient


def add_message(args, dataverse):
    r = dataverse.banner().add(args.message, args.dismissible_by_user)
    if r is not None:
        rich.print_json(data=r.json())


def remove_message(args, dataverse):
    for msg_id in args.ids:
        r = dataverse.banner().remove(msg_id)
        if r is not None:
            rich.print_json(data=r.json())


def list_messages(args, dataverse):
    r = dataverse.banner().list()
    if r is not None:
        rich.print_json(data=r.json())


def main():
    config = init()
    dataverse = DataverseClient(config['dataverse'])

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                        help='Only print command to be sent to server, but do not actually send it')

    subparsers = parser.add_subparsers()
    parser_add = subparsers.add_parser('add', help="Add a banner message")
    parser_add.add_argument('message', help="Message to add as banner, note that HTML can be included.")
    parser_add.add_argument('-d', '--dismissible-by-user', dest='dismissible_by_user', action='store_true',
                            help="Whether the user can permanently dismiss the banner")
    parser_add.set_defaults(func=lambda _: add_message(_, dataverse))

    parser_remove = subparsers.add_parser('remove', help="Remove banner messages")
    parser_remove.add_argument('ids', help="One or more ids of banner messages", nargs='+')
    parser_remove.set_defaults(func=lambda _: remove_message(_, dataverse))

    parser_list = subparsers.add_parser('list', help="List banner messages")
    parser_list.set_defaults(func=lambda _: list_messages(_, dataverse))

    args = parser.parse_args()
    dataverse.set_dry_run(args.dry_run)
    args.func(args)
