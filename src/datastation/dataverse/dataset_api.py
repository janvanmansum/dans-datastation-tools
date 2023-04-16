import json

import requests


class DatasetApi:

    def __init__(self, pid, server_url, api_token, unblock_key, safety_latch):
        self.pid = pid
        self.server_url = server_url
        self.api_token = api_token
        self.unblock_key = unblock_key
        self.safety_latch = safety_latch

    def get_pid(self):
        return self.pid

    def get_role_assignments(self, dry_run=False):
        url = f'{self.server_url}/api/datasets/:persistentId/assignments'
        params = {'persistentId': self.pid}
        headers = {'X-Dataverse-key': self.api_token}
        if dry_run:
            print("Only printing command, not sending it...")
            print(f"GET {url}")
            return None
        else:
            r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()['data']

    def add_role_assignment(self, assignee, role, dry_run=False):
        url = f'{self.server_url}/api/datasets/:persistentId/assignments'
        params = {'persistentId': self.pid}
        headers = {'X-Dataverse-key': self.api_token, 'Content-type': 'application/json'}
        role_assignment = {"assignee": assignee, "role": role}
        if dry_run:
            print("Only printing command, not sending it...")
            print(f"POST {json.dumps(role_assignment)}")
            return None
        else:
            r = requests.post(url, headers=headers, params=params, json=role_assignment)
            r.raise_for_status()
            return r

    def remove_role_assignment(self, assignment_id, dry_run=False):
        url = f'{self.server_url}/api/datasets/:persistentId/assignments/{assignment_id}'
        params = {'persistentId': self.pid}
        headers = {'X-Dataverse-key': self.api_token, 'Content-type': 'application/json'}
        if dry_run:
            print("Only printing command, not sending it...")
            print(f"DELETE {assignment_id}")
            return None
        else:
            r = requests.delete(url, headers=headers, params=params)
        r.raise_for_status()
        return r

    def is_draft(self, dry_run=False):
        url = f'{self.server_url}/api/datasets/:persistentId'
        params = {'persistentId': self.pid}
        headers = {'X-Dataverse-key': self.api_token}
        if dry_run:
            print("Only printing command, not sending it...")
            print(f"GET {url}")
            return None
        else:
            r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()['data']['latestVersion']['versionState'] == 'DRAFT'

    def delete_draft(self, dry_run=False):
        url = f'{self.server_url}/api/datasets/:persistentId'
        params = {'persistentId': self.pid}
        headers = {'X-Dataverse-key': self.api_token}
        if dry_run:
            print("Only printing command, not sending it...")
            print(f"DELETE {url}")
            return None
        else:
            r = requests.delete(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()

    def destroy(self, dry_run=False):
        url = f'{self.server_url}/api/datasets/:persistentId/destroy'
        headers = {'X-Dataverse-key': self.api_token}
        params = {'persistentId': self.pid, 'unblockKey': self.unblock_key}

        if self.safety_latch:
            print("Safety latch is on, not sending command...")
            return None
        else:
            if dry_run:
                print("Dry run, not sending command...")
                return None
            r = requests.delete(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()

    def get_metadata(self, version=':latest', dry_run=False):
        """Get the native JSON metadata for a dataset version. Version can be a number of one of ':latest', ':draft' or
         ':latest-published'. See
         https://guides.dataverse.org/en/latest/api/native-api.html#retrieving-a-dataset-version for more information.
         """
        url = f'{self.server_url}/api/datasets/:persistentId/versions/{version}'
        params = {'persistentId': self.pid}
        headers = {'X-Dataverse-key': self.api_token}
        if dry_run:
            print("Only printing command, not sending it...")
            print(f"GET {url}")
            return None
        else:
            r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()['data']
