from datastation.dataverse.banner import Banner
from datastation.dataverse.dataset import Dataset


class DataverseClient:
    """ A client for the Dataverse API. """

    def __init__(self, config: dict, dry_run: bool = False):
        self.server_url = config['server_url']
        self.api_token = config['api_token']
        self.unblock_key = config['unblock_key']
        self.dry_run = dry_run

    def set_dry_run(self, dry_run):
        self.dry_run = dry_run

    def banner(self):
        return Banner(self.server_url, self.api_token, self.unblock_key, self.dry_run)

    def dataset(self, pid):
        return Dataset(pid, self.server_url, self.api_token, self.unblock_key, self.dry_run)
