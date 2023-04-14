from datastation.dataverse.banner_api import BannerApi
from datastation.dataverse.dataset_api import DatasetApi


class DataverseClient:
    """ A client for the Dataverse API. """

    def __init__(self, config: dict, dry_run: bool = False):
        self.server_url = config['server_url']
        self.api_token = config['api_token']
        self.unblock_key = config['unblock_key']
        self.safety_latch = config['safety_latch']
        self.dry_run = dry_run

    def set_dry_run(self, dry_run):
        self.dry_run = dry_run

    def banner(self):
        return BannerApi(self.server_url, self.api_token, self.unblock_key, self.dry_run)

    def dataset(self, pid):
        return DatasetApi(pid, self.server_url, self.api_token, self.unblock_key, self.safety_latch, self.dry_run)
