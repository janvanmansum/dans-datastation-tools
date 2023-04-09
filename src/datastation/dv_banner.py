import argparse

from datastation.common.config import init
from datastation.dataverse.dataverse_client import DataverseClient


def add_message(dataverse):
    def f(args):
        dataverse.banner().add(args.message, args.dismissible_by_user)
        # todo process response and print it

    return f


def remove_message(dataverse):
    def f(args):
        for msg_id in args.ids:
            dataverse.banner().remove(msg_id)
            # todo process response and print it

    return f


def list_messages(dataverse):
    def f(_):
        dataverse.banner().list()
        # todo process response and print it

    return f


def main():
    config = init()
    dataverse = DataverseClient(config['dataverse'])

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser('add', help="Add a Banner Message")
    parser_add.add_argument('message', help="Message to add as Banner, note that HTML can be included.")
    parser_add.add_argument('-d', '--dismissible-by-user', dest='dismissible_by_user', action='store_true',
                            help="Whether the user can permanently dismiss the banner")
    parser_add.set_defaults(func=add_message(dataverse))

    parser_remove = subparsers.add_parser('remove', help="Remove Banner Message by their id-s")
    parser_remove.add_argument('ids', help="One or more ids of the Banner Message", nargs='+')
    parser_remove.set_defaults(func=remove_message(dataverse))

    parser_list = subparsers.add_parser('list', help="Get a list of active Banner Messages")
    parser_list.set_defaults(func=list_messages(dataverse))

    args = parser.parse_args()
    args.func(args)
