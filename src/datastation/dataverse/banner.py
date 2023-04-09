import logging

import requests


class Banner:

    def __init__(self, server_url: str, api_token: str, unblock_key: str, dry_run: bool = False):
        self.server_url = server_url
        self.api_token = api_token
        self.unblock_key = unblock_key
        self.dry_run = dry_run

    def list(self):
        """ List all banners. """
        url = self.server_url + '/api/admin/bannerMessage'
        headers = {'X-Dataverse-key': self.api_token}
        if self.dry_run:
            logging.info("Only printing command, not sending it...")
            logging.info(f"GET {url}")
            return None
        else:
            r = requests.get(url, headers=headers, params={'unblock-key': self.unblock_key})
            r.raise_for_status()
            print(r.text)
            return r.json()

    def add(self, msg: str, dismissible_by_user: bool = False, lang: str = 'en'):
        """ Add a banner. """
        banner = {
            "messages": [
                {
                    "lang": lang,
                    "message": msg
                }
            ],
            "dismissibleByUser": dismissible_by_user
        }
        url = self.server_url + '/api/admin/bannerMessage'
        headers = {'X-Dataverse-key': self.api_token}
        if self.dry_run:
            logging.info("Only printing command, not sending it...")
            logging.info(f"POST {banner}")
            return None
        else:
            return requests.post(url, headers=headers, params={'unblock-key': self.unblock_key}, json=banner)

    def delete(self, banner_id: int):
        """ Delete a banner. """
        url = self.server_url + '/api/admin/bannerMessage' + str(banner_id)
        headers = {'X-Dataverse-key': self.api_token}
        if self.dry_run:
            logging.info("Only printing command, not sending it...")
            logging.info(f"DELETE {url}")
            return None
        else:
            return requests.delete(url, headers=headers, params={'unblock-key': self.unblock_key})
