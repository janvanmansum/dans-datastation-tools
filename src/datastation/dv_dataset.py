import time
import requests
import logging

from datastation.dv_api import get_dataset_locks, reingest_file, get_dataset_files
from typing import Optional

class DataverseAPI:

    def __init__(self, server_url, api_token, logger: logging.Logger):
        self.server_url = server_url
        self.api_token = api_token
        self.logger = logger

    def get_dataset_files(self, pid: str, version=':latest'):
        return get_dataset_files(self.server_url, pid, version)
        
    def get_dataset_locks(self, pid: str):
        return get_dataset_locks(self.server_url, pid)

    def reingest_file(self, file_id: str):
        return reingest_file(self.server_url, self.api_token, file_id)


class FileReingester():

    def __init__(self, dataverse_api: DataverseAPI, logger: logging.Logger, poll_interval_seconds: int):
        self.dataverse_api = dataverse_api
        self.logger = logger
        self.poll_interval_seconds = poll_interval_seconds

    def reingest_dataset_tabular_files(self, pid):
        try:
            file_list = self.dataverse_api.get_dataset_files(pid)

            for dataset_file in file_list:
                file_id = dataset_file['dataFile']['id']
                self._reingest_file(str(pid), str(file_id))

        except requests.exceptions.RequestException as re:
            if re.response.status_code == 404:
                self.logger.error('[%s] Dataset not found', pid)
                return
            
            raise

    def _reingest_file(self, pid: str, file_id: str):
        self.logger.info('[%s] Reingesting file: %s', pid, file_id)

        try:
            reingest_response = self.dataverse_api.reingest_file(file_id)
        
            # if the ingest actually started, the message is 'Datafile 6 queued for ingest'
            message = reingest_response.get('message', '')

            if 'queued for ingest' not in message:
                self.logger.info('[%s] Reingest not started: %s', pid, message)
                return

            self.logger.info('[%s] Reingest started: %s; waiting for dataset locks to clear', pid, message)

            while True:
                locks = self.dataverse_api.get_dataset_locks(pid)
                self.logger.debug('[%s] Dataset is locked: %s locks present', pid, len(locks))
                            
                if len(locks) == 0:
                    self.logger.debug('[%s] Dataset is unlocked', pid)
                    break

                time.sleep(self.poll_interval_seconds)
            
            self.logger.info('[%s] Reingest complete for file id %s', pid, file_id)

        except requests.exceptions.RequestException as re:
            self.logger.debug('[%s] RequestException: %s', pid, re.response.json())
            return


def reingest_files(server_url: str, api_token: str, pid: Optional[str], pid_file: Optional[str], poll_interval_seconds: Optional[int] = 2):
    logger = logging.getLogger('dv_dataset')

    manager = DataverseAPI(server_url, api_token, logger)
    reingester = FileReingester(manager, logger, poll_interval_seconds=poll_interval_seconds)

    pids = []

    if pid is not None:
        pids = [pid]
    
    elif pid_file is not None:
        try:
            with open(pid_file, 'r') as f:
                pids = [line.strip() for line in f]
                
        except FileNotFoundError as e:
            logger.error('File not found: %s (system message: %s)', pid_file, e.strerror)
            return
        
    for pid in pids:
        if len(pid) == 0:
            continue
        
        try:
            reingester.reingest_dataset_tabular_files(pid)
        except Exception as e:
            logger.exception('[%s] Error reingesting dataset files: %s', pid, e)
            continue

                

