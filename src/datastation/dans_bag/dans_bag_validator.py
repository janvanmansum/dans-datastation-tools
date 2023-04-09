import json
import logging
import os
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

import requests
import yaml

from datastation.common.find_bags import find_bags
from datastation.common.result_writer import ResultWriter


class DansBagValidator:
    def __init__(self, config: dict, accept_type: str = 'application/json', dry_run: bool = False):
        self.server_url = config['service_base_url']
        self.accept_type = accept_type
        self.dry_run = dry_run

    def validate(self, path: str, info_package_type: str, result_writer: ResultWriter):
        try:
            is_first = True
            for bag in find_bags(path):
                self.validate_dans_bag(bag, info_package_type, result_writer, is_first)
                is_first = False
        finally:
            result_writer.close()

    def validate_dans_bag(self, path: str, info_package_type: str, result_writer: ResultWriter, is_first: bool = True):
        logging.info("Validating bag: {}".format(path))
        command = {
            'bagLocation': os.path.abspath(path),
            'packageType': info_package_type,
        }

        msg = MIMEMultipart("form-data")
        p = MIMEApplication(json.dumps(command), "json", _encoder=encoders.encode_noop)
        p.add_header("Content-Disposition", "form-data; name=command")
        msg.attach(p)

        body = msg.as_string().split('\n\n', 1)[1]
        headers = dict(msg.items())
        headers.update({'Accept': self.accept_type})

        if self.dry_run:
            logging.info("Only printing command, not sending it...")
            print(msg.as_string())
        else:
            r = requests.post('{}/validate'.format(self.server_url), data=body,
                              headers=headers)
            if self.accept_type == 'application/json':
                result = json.loads(r.text)
            elif self.accept_type == 'text/plain':
                result = yaml.safe_load(r.text)
            else:
                raise Exception("Unknown accept type: {}".format(self.accept_type))

            result_writer.write(result, is_first)
