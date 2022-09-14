import argparse
import os

import requests
from builtins import all
import stat

service_baseurl = 'http://localhost:20300'

file_writeable_to_group = lambda f: os.stat(f).st_mode & stat.S_IWGRP > 0

def start_import(path, continue_previous, is_migration):
    if not has_dirtree_pred(path, file_writeable_to_group):
        chmod_command = "chmod -R g+w %s" % path
        print("Some files in the import batch do not give the owner group write permissions. Executing '%s' to fix it" % chmod_command)
        status = os.system(chmod_command)
        if status != 0:
            print("Could not give owner group write permissions. Possibly your account is not the owner user of the files.")
            return
    print("Sending start import request to server...")
    r = requests.post('%s/%s/:start' % (service_baseurl, "migrations" if is_migration else "imports"), json={
        'batch': os.path.abspath(path),
        'continue': continue_previous
    })
    print('Server responded: %s' % r.text)

#
# Helper functions
#
def has_file_pred(file, pred):
    return pred(file)

def has_dirtree_pred(dir, pred):
    for root, dirs, files in os.walk(dir):
        return pred(root) \
               and all(pred(os.path.join(root, dir)) for dir in dirs) \
               and all(pred(os.path.join(root, file)) for file in files)

def list_events(params):
    r = requests.get('%s/events' % service_baseurl, headers={'Accept': 'text/csv'}, params=params)
    print(r.text)
