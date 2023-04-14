import json
import logging

import requests


class BannerApi:

    def __init__(self, server_url: str, api_token: str, unblock_key: str, dry_run: bool = False):
        self.server_url = server_url
        self.api_token = api_token
        self.unblock_key = unblock_key
        self.dry_run = dry_run

    def list(self):
        """ List all banners. """
        url = f'{self.server_url}/api/admin/bannerMessage'
        headers = {'X-Dataverse-key': self.api_token}
        if self.dry_run:
            logging.info("Only printing command, not sending it...")
            logging.info(f"GET {url}")
            return None
        else:
            r = requests.get(url, headers=headers, params={'unblock-key': self.unblock_key})
            r.raise_for_status()
            return r

    def add(self, msg: str, dismissible_by_user: bool = False, lang: str = 'en'):
        """ Add a banner. """
        banner = {
            "messageTexts": [
                {
                    "lang": lang,
                    "message": msg
                }
            ],
            "dismissibleByUser": str(dismissible_by_user).lower()
        }
        url = f'{self.server_url}/api/admin/bannerMessage'
        headers = {'X-Dataverse-key': self.api_token, 'Content-type': 'application/json'}
        if self.dry_run:
            print("Only printing command, not sending it...")
            print(f"POST {json.dumps(banner)}")
            return None
        else:
            r = requests.post(url, headers=headers, params={'unblock-key': self.unblock_key}, json=banner)
            r.raise_for_status()
            return r

    def remove(self, banner_id: int):
        """ Remove a banner. """
        url = f'{self.server_url}/api/admin/bannerMessage/{banner_id}'
        headers = {'X-Dataverse-key': self.api_token}
        if self.dry_run:
            print("Only printing command, not sending it...")
            print(f"DELETE {url}")
            return None
        else:
            r = requests.delete(url, headers=headers, params={'unblock-key': self.unblock_key})
            r.raise_for_status()
            return r
