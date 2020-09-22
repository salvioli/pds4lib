#!/usr/bin/env python3

from pathlib import Path
from lxml import etree as et

ns = {'pds': "http://pds.nasa.gov/pds4/pds/v1"}
for prefix, namespace_uri in ns.items():
    et.register_namespace(prefix, namespace_uri)


def strip_if_has_text(element):
    if isinstance(element, list):
        for m in element:
            strip_if_has_text(m)
    elif element.text is not None:
        element.text = element.text.strip()


class ContextLabel:

    def __init__(self, label_file):
        self.path = label_file
        self.xml_tree = et.parse(str(self.path))
        self.type = self.xml_tree.getroot().tag

    @property
    def vid(self):
        return self.get(".//pds:version_id").text

    @property
    def lid(self):
        return self.get(".//pds:logical_identifier").text

    def set(self, xpath_selector, value):
        self.get(xpath_selector).text = value

    def set_all(self, xpath_selector, values):
        if not isinstance(values, list):
            values = [values]
        n_values = len([v for v in values if v is not None])
        attrs = self.get_all(xpath_selector)
        assert len(attrs) >= n_values, f"{self.path}: {attrs} should be set to {values} but there are not enough values to set"
        for a, v in zip(attrs, values):
            if v is not None:
                a.text = str(v)

    def get(self, xpath_selector):
        matches = self.xml_tree.getroot().find(xpath_selector, namespaces=ns)
        strip_if_has_text(matches)
        return matches

    def get_all(self, xpath_selector):
        matches = self.xml_tree.getroot().findall(xpath_selector, namespaces=ns)
        strip_if_has_text(matches)
        return matches


class Label(ContextLabel):

    @property
    def checksums(self):
        return [chk.text for chk in self.get_all(".//pds:md5_checksum")]

    @checksums.setter
    def checksums(self, values):
        self.set_all('.//pds:md5_checksum', values)

    @property
    def records(self):
        return [int(records.text) for records in self.get_all(".//pds:records")]

    @records.setter
    def records(self, values):
        self.set_all('.//pds:records', values)

    @property
    def data_file_sizes(self):
        return [float(size.text) for size in self.get_all(".//pds:file_size")]

    @data_file_sizes.setter
    def data_file_sizes(self, values):
        self.set_all('.//pds:file_size', values)

    @property
    def data_files(self):
        files = self.get_all('.//pds:file_name')
        files = [self.path.parent / f.text for f in files]
        return files

    def write(self):
        self.xml_tree.write(str(self.path), xml_declaration=True, encoding='UTF-8', pretty_print=True)
