import logging
import time

import os


def get_pids(pid_or_file):
    if os.path.isfile(os.path.expanduser(pid_or_file)):
        pids = []
        with open(os.path.expanduser(pid_or_file)) as f:
            for line in f:
                pids.append(line.strip())
        return pids
    else:
        return [pid_or_file]


class BatchProcessor:
    def __init__(self, delay=0.1, fail_on_first_error=True):
        self.delay = delay
        self.fail_on_first_error = fail_on_first_error

    def set_delay(self, delay):
        self.delay = delay

    def set_fail_on_first_error(self, fail_on_first_error):
        self.fail_on_first_error = fail_on_first_error

    def process_pids(self, pids, callback):
        num_pids = len(pids)
        logging.info(f"Start batch processing on {num_pids} pids")
        i = 0
        for pid in pids:
            i += 1
            try:
                logging.info(f"Processing {i} of {num_pids}: {pid}")
                callback(pid)
                time.sleep(self.delay)
            except Exception as e:
                logging.exception("Exception occurred", exc_info=True)
                if self.fail_on_first_error:
                    logging.error(f"Stop processing because of an exception: {e}")
                    break
                logging.debug("fail_on_first_error is False, continuing...")
