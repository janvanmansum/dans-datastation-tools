import argparse
import os, grp
import shutil

import requests
from builtins import all
import stat

file_writeable_to_group = lambda f: os.stat(f).st_mode & stat.S_IWGRP > 0

def start_import(service_baseurl, path, continue_previous, is_migration):
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

def list_events(service_baseurl, params):
    r = requests.get('%s/events' % service_baseurl, headers={'Accept': 'text/csv'}, params=params)
    print(r.text)

def set_permissions(dir, dir_mode, file_mode, group):
    for root, dirs, files in os.walk(dir):
        for d in [root] + dirs:
            os.chmod(d, dir_mode)
            shutil.chown(d, group=group)
        for f in files:
            os.chmod(f, file_mode)
            shutil.chown(f, group=group)


