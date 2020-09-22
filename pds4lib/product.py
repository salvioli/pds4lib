import csv
import os
import warnings
from abc import ABCMeta, abstractmethod
from pathlib import Path
from pds4lib import Label, DataFile
import lxml.etree as et
import re

type_map = {
    "Product_Context": "NullProduct",
}


class Product(metaclass=ABCMeta):
    @staticmethod
    def create(label):
        class_type = Product._get_product_type(label)
        class_type = type_map.get(class_type, "DataFileProduct")
        return globals()[class_type](label)

    @staticmethod
    def _get_product_type(label):
        class_type = et.parse(str(label)).getroot().tag
        class_type = re.sub(r"\{.*\}", "", class_type)
        return class_type

    def __init__(self, label):
        assert isinstance(label, (str, os.PathLike)), f"{label} needs to be a string or a path-like object"

        if isinstance(label, str):
            label = Path(label)

        if not label.is_file():
            raise FileDoesNotExistError(f"{label} is not a valid file")

        self.label = Label(label)

    @abstractmethod
    def get(self, xpath_selector):
        pass

    @abstractmethod
    def write(self, out):
        pass

    @abstractmethod
    def update(self):
        pass

    @property
    def vid(self):
        return self.label.vid

    @property
    def path(self):
        return self.label.path

    @property
    def lid(self):
        return self.label.lid


class NullProduct(Product):
    def write(self):
        pass

    def update(self):
        pass

    def update(self):
        pass

    def get(self, xpath_selector):
        pass


class DataFileProduct(Product):
    def __init__(self, label):
        super(DataFileProduct, self).__init__(label)

        for f in self.label.data_files:
            if not f.is_file():
                raise FileDoesNotExistError(f"{self.label.path}: references {f} which cannot be found")

        self.data_files = [DataFile.create(f) for f in self.label.data_files]

    def _update_label(self):
        # for i, df in enumerate(self.data_files):
            # self.label.checksums[i] = df.checksum
            # self.label.data_file_sizes[i] = df.size
            # self.label.records[i] = df.records

        if len(self.label.checksums) > 0:
            self._update_checksums()
        if len(self.label.records) > 0:
            self._update_records_number()
        if len(self.label.data_file_sizes) > 0:
            self._update_data_file_sizes()

        self.label.write()

    def _update_checksums(self):
        self.label.checksums = [df.checksum for df in self.data_files]

    def _update_data_file_sizes(self):
        self.label.data_file_sizes = [df.size for df in self.data_files]

    def _update_records_number(self):
        self.label.records = [df.records for df in self.data_files]

    def update(self):
        print(f'updating product {self.path}')
        self._update_label()
        super().update()

    def get(self, xpath_selector):
        return self.label.get(xpath_selector)

    def write(self):
        self.label.write()
        for df, ldf in zip(self.data_files, self.label.data_files):
            df.write()


class EmptyCollectionDirectoryWarning(UserWarning):
    pass


class FileDoesNotExistError(Exception):
    pass


class DirectoryDoesNotExistError(Exception):
    pass


class Collection(DataFileProduct):

    @staticmethod
    def _build_data_file_record(labl):
        return f"P, {labl.lid}::{labl.vid}\r\n"

    def __init__(self, collection_label):
        super(Collection, self).__init__(collection_label)
        assert len(self.data_files) == 1
        if not len(self.get_labels()) > 0:
            warnings.warn(f'No product found in {self.path}', category=EmptyCollectionDirectoryWarning)

    def get_labels(self):
        files = list(self.path.parent.rglob('*.xml'))
        return [file for file in files if not file.name.startswith('collection')]

    def update(self):
        self.update_products()
        self.update_data_file()
        super().update()

    def update_data_file(self):
        with open(self.data_files[0].path, 'r', newline='\r\n') as f:
            members = list(csv.reader(f, delimiter=','))
            members = [[e.strip() for e in line] for line in members]
            secondary_members = [", ".join(m) for m in members if m[0] == "S"]
            secondary_members = [' '.join(string.split()) + '\r\n' for string in secondary_members]

        collection_products_records = [self._build_data_file_record(Label(lbl)) for lbl in self.get_labels()]
        output = secondary_members + collection_products_records
        output = ''.join(str(line) for line in output)
        self.data_files[0].data = output
        self.data_files[0].write()

    def update_products(self):
        [Product.create(p).update() for p in self.get_labels()]
