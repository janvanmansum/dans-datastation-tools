import json
import os

# Start - XML related stuff, maybe not needed
from lxml import etree
import dicttoxml


# check if we can also write xml instead of json!
def get_xml_output(data):
    # should do dict to xml
    xml = dicttoxml.dicttoxml(data, custom_root='dataset')  # create_xml_tree(etree.Element("root"), data)
    xml_dom = etree.fromstring(xml)
    return etree.tostring(xml_dom, pretty_print=True)


def store_dataset_result_as_xml(pid, dataset_metadata, save_path):
    # construct filename from pid
    # pid = dataset_json['global_id']
    filename_base = pid.replace(':', '_')
    filename_base = filename_base.replace('/', '_')
    filename_ext = 'xml'
    filename = filename_base + '.' + filename_ext
    full_name = os.path.join(save_path, filename)
    with open(full_name, "wb") as outfile:
        outfile.write(get_xml_output(dataset_metadata))
    return


# End - XML related stuff

def construct_filename_base_from_pid(pid):
    filename_base = pid.replace(':', '_')
    filename_base = filename_base.replace('/', '_')
    return filename_base


def get_json_output(data):
    return json.dumps(data, indent=2)


# note that search results don't contain all metadata, especially it is lacking the custom blocks!
def store_dataset_result(pid, dataset_metadata, save_path):
    # construct filename from pid
    # pid = dataset_json['global_id']
    filename_base = construct_filename_base_from_pid(pid)
    filename_ext = 'json'
    filename = filename_base + '.' + filename_ext
    full_name = os.path.join(save_path, filename)
    with open(full_name, "w") as outfile:
        outfile.write(get_json_output(dataset_metadata))
    return
