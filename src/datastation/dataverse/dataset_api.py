import json

import requests


class DatasetApi:

    def __init__(self, pid, server_url, api_token, unblock_key, dry_run):
        self.pid = pid
        self.server_url = server_url
        self.api_token = api_token
        self.unblock_key = unblock_key
        self.dry_run = dry_run

    def get_pid(self):
        return self.pid

    def get_role_assignments(self):
        url = f'{self.server_url}/api/datasets/:persistentId/assignments'
        params = {'persistentId': self.pid}
        headers = {'X-Dataverse-key': self.api_token}
        if self.dry_run:
            print("Only printing command, not sending it...")
            print(f"GET {url}")
            return None
        else:
            r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()['data']

    def add_role_assignment(self, assignee, role):
        url = f'{self.server_url}/api/datasets/:persistentId/assignments'
        params = {'persistentId': self.pid}
        headers = {'X-Dataverse-key': self.api_token, 'Content-type': 'application/json'}
        role_assignment = {"assignee": assignee, "role": role}
        if self.dry_run:
            print("Only printing command, not sending it...")
            print(f"POST {json.dumps(role_assignment)}")
            return None
        r = requests.post(url, headers=headers, params=params, json=role_assignment)
        r.raise_for_status()
        return r

    def remove_role_assignment(self, assignment_id):
        url = f'{self.server_url}/api/datasets/:persistentId/assignments/{assignment_id}'
        params = {'persistentId': self.pid}
        headers = {'X-Dataverse-key': self.api_token, 'Content-type': 'application/json'}
        if self.dry_run:
            print("Only printing command, not sending it...")
            print(f"DELETE {assignment_id}")
            return None
        else:
            r = requests.delete(url, headers=headers, params=params)
        r.raise_for_status()
        return r
