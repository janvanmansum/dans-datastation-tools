import argparse

import os

from datastation.batch_processing import batch_process
from datastation.config import init
from datastation.ds_metadatafile import store_dataset_result
from datastation.ds_pidsfile import load_pids
from datastation.dv_api import get_dataset_metadata_export


def retrieve_dataset_metadata_action(server_url, pid, output_dir):
    dataset_metadata = get_dataset_metadata_export(server_url, pid)
    # note that the dataset metadata might be large if there are a lot of files in the dataset!
    store_dataset_result(pid, dataset_metadata, output_dir)
    # store_dataset_result_as_xml(pid, dataset_metadata, save_path)


def retrieve_dataset_metadata_command(config, input_filename, output_dir):
    print('Args: ' + input_filename + ',  ' + output_dir)
    print("Example using server URL: " + config['dataverse']['server_url'])

    # create output dir if not exists!
    #work_path = os.path.dirname(CONFIG.OUTPUT_DIR)
    save_path = os.path.join(config['files']['output_dir'], output_dir)
    if os.path.isdir(save_path):
        print("Skipping dir creation, because it already exists: " + save_path)
    else:
        print("Creating output dir: " + save_path)
        os.makedirs(save_path)

    # look for inputfile in configured OUTPUT_DIR
    full_name = os.path.join(config['files']['output_dir'], input_filename)
    pids = load_pids(full_name)

    batch_process(pids, lambda pid: retrieve_dataset_metadata_action(config['dataverse']['server_url'], pid, save_path), config['files']['output_dir'], delay=0.2)



def main():
    config = init()
    parser = argparse.ArgumentParser(description='Retrieves the metadata for all published datasets with the pids in the given inputfile')
    parser.add_argument('-p', '--pids-file', default='dataset_pids.txt', help='The input file with the dataset pids')
    parser.add_argument('-o', '--output', default='dataset_metadata', help='The output dir, for storing the metadata files retrieved')
    args = parser.parse_args()

    retrieve_dataset_metadata_command(config, args.pids_file, args.output)

if __name__ == '__main__':
    main()
