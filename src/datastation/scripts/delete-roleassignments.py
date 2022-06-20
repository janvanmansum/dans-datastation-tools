import argparse
import os

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.ds_pidsfile import load_pids
from datastation.dv_api import delete_dataset_role_assignment, get_dataset_roleassigments


def delete_roleassignment_action(server_url, api_token, pid, role_assignee, role_alias):
    deleted_role = False
    resp_data = get_dataset_roleassigments(server_url, api_token, pid)
    # print(json.dumps(resp_data, indent=2))
    for role_assignment in resp_data:
        assignee = role_assignment['assignee']
        # role_id = role_assignment['roleId']
        alias = role_assignment['_roleAlias']
        print("Role assignee: " + assignee + ', role alias: ' + alias)
        if assignee == role_assignee and alias == role_alias:
            # delete this one
            assignment_id = role_assignment['id']
            print("Try deleting the role assignment")
            delete_dataset_role_assignment(server_url, api_token, pid, assignment_id)
            print("Done")
            deleted_role = True
        else:
            print("Leave as-is")
    return deleted_role


def delete_roleassignments_command(config, pids_file, role_assignee, role_alias):
    # look for inputfile in configured OUTPUT_DIR
    full_name = os.path.join(config['files']['output_dir'], pids_file)
    pids = load_pids(full_name)

    # could be fast, but depends on number of files inside the dataset
    batch_process(pids, lambda pid: delete_roleassignment_action(config['dataverse']['server_url'],
                                                                 config.DATAVERSE_API_TOKEN, pid, role_assignee,
                                                                 role_alias), config['files']['output_dir'], delay=1.5)


def main():
    config = init()
    parser = argparse.ArgumentParser(
        description='Delete role assigment for datasets with the pids in the given inputfile')
    parser.add_argument("role_assignee", help="Role assignee (example: @dataverseAdmin)")
    parser.add_argument("role_alias", help="Role alias (example: contributor")
    parser.add_argument('-p', '--pids_file', default='dataset_pids.txt', help='The input file with the dataset pids')
    args = parser.parse_args()

    role_assignee = args.role_assignee
    role_alias = args.role_alias

    delete_roleassignments_command(config, args.pids_file, role_assignee, role_alias)


if __name__ == '__main__':
    main()
