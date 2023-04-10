import json

import requests


class Dataset:

    def __init__(self, pid, server_url, api_token, unblock_key, dry_run):
        self.pid = pid
        self.server_url = server_url
        self.api_token = api_token
        self.unblock_key = unblock_key
        self.dry_run = dry_run

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
        return r

    def add_role_assignment(self, role_assignment):
        url = f'{self.server_url}/api/datasets/:persistentId/assignments'
        params = {'persistentId': self.pid}
        headers = {'X-Dataverse-key': self.api_token, 'Content-type': 'application/json'}
        if self.dry_run:
            print("Only printing command, not sending it...")
            print(f"POST {json.dumps(role_assignment)}")
            return None
        r = requests.post(url, headers=headers, params=params, json=role_assignment)
        r.raise_for_status()
        return r

    def delete_role_assignment(self, role_assignment):
        url = f'{self.server_url}/api/datasets/:persistentId/assignments'
        params = {'persistentId': self.pid}
        headers = {'X-Dataverse-key': self.api_token, 'Content-type': 'application/json'}
        if self.dry_run:
            print("Only printing command, not sending it...")
            print(f"DELETE {json.dumps(role_assignment)}")
            return None
        else:
            r = requests.delete(url, headers=headers, params=params, json=role_assignment)
        r.raise_for_status()
        return r
