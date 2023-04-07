# module for result writer classes

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
        self.out_stream.write(yaml.dump([result]))


class CsvResultWriter:
    def __init__(self, out_stream: typing.TextIO):
        self.out_stream = out_stream
    