# module for result writer classes
import csv
import json
import typing

import yaml


# Function that write a result in the form of a dictionary to a text stream
class JsonResultWriter:
    def __init__(self, out_stream: typing.TextIO):
        self.out_stream = out_stream

    def write(self, result: dict, is_first: bool):
        if not is_first:
            self.out_stream.write(", ")
        self.out_stream.write(json.dumps(result))


class YamlResultWriter:
    def __init__(self, out_stream: typing.TextIO):
        self.out_stream = out_stream

    def write(self, result: dict, is_first: bool):
        self.out_stream.write(yaml.dump(result))


class CsvResultWriter:
    def __init__(self, headers: list, out_stream: typing.TextIO):
        self.out_stream = out_stream
        self.headers = headers
        self.csv_writer = csv.DictWriter(out_stream, fieldnames=headers, lineterminator="\n")
        self.csv_writer.writeheader()

    def write(self, result: dict, is_first: bool):
        # Check if the result has the same keys as the headers
        if len(result.keys()) > 0:
            if set(result.keys()) != set(self.headers):
                raise ValueError("Result keys do not match headers")
            else:
                self.csv_writer.writerow(result)
