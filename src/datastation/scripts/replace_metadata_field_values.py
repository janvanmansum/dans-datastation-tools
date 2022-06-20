import argparse
import os

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.ds_pidsfile import load_pids

from datastation.dv_api import replace_dataset_metadatafield, get_dataset_metadata


def replace_metadata_field_value_action(server_url, api_token, pid, mdb_name, field_name, field_from_value,
                                        field_to_value):
    """

    :param pid:
    :param mdb_name:
    :param field_name:
    :param field_from_value:
    :param field_to_value:
    :return:
    """
    # Getting the metadata is not always needed when doing a replace,
    # but when you need to determine if replace is needed by inspecting the current content
    # you need to 'get' it first.
    # Another approach would be to do that selection up front (via search)
    # and have that generate a list with pids to process 'blindly'.
    resp_data = get_dataset_metadata(server_url, api_token, pid)
    # print(resp_data['datasetPersistentId'])
    mdb_fields = resp_data['metadataBlocks'][mdb_name]['fields']
    # print(json.dumps(mdb_fields, indent=2))

    # metadata field replacement (an idempotent action I think)
    # replace replace_from with replace_to for field with typeName replace_field
    replace_field = field_name
    replace_from = field_from_value
    replace_to = field_to_value

    replaced = False
    for field in mdb_fields:
        # expecting (assuming) one and only one instance,
        # but the code will try to change all it can find
        if field['typeName'] == replace_field:
            print("Found " + replace_field + ": " + field['value'])
            if field['value'] == replace_from:
                updated_field = field.copy()
                # be save and mutate a copy
                updated_field['value'] = replace_to
                print("Try updating it with: " + updated_field['value'])
                replace_dataset_metadatafield(server_url, api_token, pid, updated_field)
                print("Done")
                replaced = True
            else:
                print("Leave as-is")
    return replaced


def replace_metadata_field_value_command(config, server_url, api_token, pids_file, mdb_name, field_name,
                                         field_from_value, field_to_value):
    # look for inputfile in configured OUTPUT_DIR
    full_name = os.path.join(config['files']['output_dir'], pids_file)
    pids = load_pids(full_name)

    batch_process(pids,
                  lambda pid: replace_metadata_field_value_action(server_url, api_token, pid, mdb_name, field_name,
                                                                  field_from_value,
                                                                  field_to_value), config['files']['output_dir'],
                  delay=5.0)


# Note that the datasets that got changed get into a DRAFT status
# and at some point need to be published with a minor version increment.
# This is not done here, because you might want several (other) changes
# on the same datasets before publishing.
def main():
    config = init()
    parser = argparse.ArgumentParser(
        description='Replace metadata field in datasets with the pids in the given inputfile')
    parser.add_argument("metadatablock_name", help="Name of the metadata block")
    parser.add_argument("field_name", help="Name of the field (json typeName)")
    parser.add_argument("field_from_value", help="Value to be replaced")
    parser.add_argument("field_to_value", help="Value replacing (the new value)")
    parser.add_argument('-p', '--pids_file', default='dataset_pids.txt', help='The input file with the dataset pids')
    args = parser.parse_args()

    # have a look at the json metadata export (dataverse_json) to see what names are possible
    mdb_name = 'citation'
    field_name = 'title'
    field_from_value = 'test1'
    field_to_value = 'test1-X'

    # use config for server url and api token
    server_url = config['dataverse']['server_url']
    api_token = config.DATAVERSE_API_TOKEN

    replace_metadata_field_value_command(config, server_url, api_token, args.pids_file, mdb_name, field_name,
                                         field_from_value, field_to_value)


if __name__ == '__main__':
    main()
