import os
from os.path import exists
from shutil import copyfile
import yaml
from pkgutil import get_data
import logging


def ensure_config_yml_exists(config_yml, example_config_yml):
    if not exists(config_yml):
        print("No config.yml found; copying example-config.yml to config.yml")
        with open('config.yml', 'wb') as f:
            example_cfg = get_data('datastation', 'example-config.yml')
            if example_cfg is None:
                print("WARN: cannot find example-config.yml")
            else:
                f.write(get_data('datastation', example_config_yml))


def init():
    """
    Initialization function to run by each script. It creates the work directory if it doesn't exist yet, and it reads
    config.yml. If `config.yml` does not exist yet, then it is first created from `example-config.yml`.

    Returns:
        a dictionary with the configuration settings
    """
    # logging.basicConfig(level=logging.INFO, filename='data/utils.log',
    #                     format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', filemode='w',
    #                     encoding='UTF-8')
    #
    # work_path = 'data'
    # if os.path.isdir(work_path):
    #     logging.info(msg=("Skipping dir creation, because it already exists: %", work_path))
    # else:
    #     logging.info(msg=("Creating work dir: %", work_path))
    #     os.makedirs(work_path)

    ensure_config_yml_exists('config.yml', 'example-config.yml')
    with open('config.yml', 'r') as stream:
        config = yaml.safe_load(stream)
        return config
