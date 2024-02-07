from datastation.common.result_writer import CsvResultWriter, YamlResultWriter, JsonResultWriter
from datastation.dataverse.dataverse_client import DataverseClient
import logging
import re
import csv
import sys
import json
import rich
from datetime import timedelta


class PermissionsCollect:

    def __init__(self, dataverse_client: DataverseClient, output_file, output_format, dry_run: bool = False):
        self.dataverse_client = dataverse_client
        self.output_file = output_file
        self.output_format = output_format
        self.dry_run = dry_run

        self.writer = None
        self.is_first = True  # Would be nicer if the Writer does the bookkeeping

    def create_result_writer(self, out_stream):
        logging.info(f'Writing output: {self.output_file}, with format : {self.output_format}')
        csv_columns = ['depth', 'parentalias', 'alias', 'name', 'groups', 'roles', 'assignments']
        if self.output_format == 'csv':
            return CsvResultWriter(headers=csv_columns, out_stream=out_stream)
        else:
            return JsonResultWriter(out_stream)

    def write_result_row(self, row):
        self.writer.write(row, self.is_first)
        self.is_first = False  # Only the first time it can be True

    def get_result_row(self, parent_alias, child_alias, child_name, depth):
        logging.info(f'Retrieving permission info for dataverse: {parent_alias} / {child_alias} ...')
        group_info = self.get_group_info(child_alias)
        role_info = self.get_role_info(child_alias)
        assignment_info = self.get_assignment_info(child_alias)
        row = {'depth': depth, 'parentalias': parent_alias, 'alias': child_alias, 'name': child_name,
               'groups': group_info, 'roles': role_info, 'assignments': assignment_info}
        return row

    def get_group_info(self, alias):
        resp_data = self.dataverse_client.dataverse().get_groups(alias)
        # flatten and compact it... no list comprehension though
        result_list = []
        for group in resp_data:
            #  append the number of assignees in braces
            result_list.append(group['identifier'] + ' (' + str(len(group['containedRoleAssignees'])) + ')')
        return ', '.join(result_list)

    def get_role_info(self, alias):
        resp_data = self.dataverse_client.dataverse().get_roles(alias)
        # flatten and compact it... no list comprehension though
        result_list = []
        for role in resp_data:
            #  append the number of permissions in braces
            result_list.append(role['alias'] + ' (' + str(len(role['permissions'])) + ')')
        return ', '.join(result_list)

    def get_assignment_info(self, alias):
        resp_data = self.dataverse_client.dataverse().get_assignments(alias)
        # flatten and compact it... no list comprehension though
        result_list = []
        for assignment in resp_data:
            #  append the role alias in braces
            result_list.append(assignment['assignee'] + ' (' + (assignment['_roleAlias']) + ')')
        return ', '.join(result_list)


    # Traverses the tree and collects permissions info for each dataverse using recursion.
    def collect_children_permissions_info(self, parent_data, depth=1):
        parent_alias = parent_data['alias']
        # Only direct descendants (children)
        if 'children' in parent_data:
            for child_data in parent_data['children']:
                row = self.get_result_row(parent_alias, child_data['alias'], child_data['name'], depth)
                self.write_result_row(row)
                self.collect_children_permissions_info(child_data, depth + 1)  # Recurse

    def collect_permissions_info(self):
        out_stream = sys.stdout
        if self.output_file != '-':
            try:
                out_stream = open(self.output_file, "w")
            except:
                logging.error(f"Could not open file: {self.output_file}")
                raise

        self.writer = self.create_result_writer(out_stream)

        logging.info(f'Extracting tree for server: {self.dataverse_client.server_url} ...')
        tree_data = self.dataverse_client.metrics().get_tree()
        alias = tree_data['alias']
        name = tree_data['name']
        logging.info(f'Extracted the tree for the toplevel dataverse: {name} ({alias})')

        logging.info("Retrieving the info for this dataverse instance...")
        row = self.get_result_row("-", alias, name, 0)  # The root has no parent
        self.write_result_row(row)

        self.collect_children_permissions_info(tree_data, 1)
        self.writer.close()
        self.is_first = True
