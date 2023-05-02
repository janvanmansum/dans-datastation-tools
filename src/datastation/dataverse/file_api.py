import requests


class FileApi:

    def __init__(self, id, server_url, api_token, unblock_key, safety_latch):
        self.id = id
        self.server_url = server_url
        self.api_token = api_token
        self.unblock_key = unblock_key
        self.safety_latch = safety_latch

    def reingest(self):
        url = f'{self.server_url}/api/files/{self.id}/reingest'
        params = {'key': self.unblock_key}
        headers = {'X-Dataverse-key': self.api_token}
        r = requests.post(url, headers=headers, params=params)
        r.raise_for_status()
        return r
