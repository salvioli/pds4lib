import hashlib as hash
from abc import ABCMeta, abstractmethod
from pathlib import Path
import chardet

type_map = {
    ".csv": "RecordsTextDataFile",
    ".tab": "RecordsTextDataFile",
    ".txt": "TextDataFile",
    ".dat": "BinaryDataFile",
    ".pdf": "BinaryDataFile",
    ".sch": "RecordsTextDataFile",
    ".xsd": "RecordsTextDataFile",
    "default": 'BinaryDataFile',
}


class DataFile(metaclass=ABCMeta):
    @staticmethod
    def create(file):
        extension = Path(file).suffix
        class_type = type_map.get(extension, type_map['default'])
        return globals()[class_type](file)

    def __init__(self, data_file_path):
        if isinstance(data_file_path, str):
            data_file_path = Path(data_file_path)

        self.path = data_file_path
        self.read_data()

    @property
    def size(self):
        return self.path.stat().st_size

    @property
    def checksum(self):
        h = hash.md5()
        with open(self.path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    @abstractmethod
    def read_data(self):
        pass

    @abstractmethod
    def write(self):
        pass

    @property
    def records(self):
        pass


class BinaryDataFile(DataFile):
    def __init__(self, data_file_path):
        super(BinaryDataFile, self).__init__(data_file_path)

    def read_data(self):
        self.data = self.path.read_bytes()
        return self.data

    def write(self):
        with open(self.path, "wb") as f:
            f.write(self.data)


class TextDataFile(DataFile):
    def __init__(self, data_file_path):
        super(TextDataFile, self).__init__(data_file_path)

    def read_data(self):
        res = chardet.detect(self.path.read_bytes())
        self.data = self.path.read_text(encoding=res['encoding'])
        return self.data

    def write(self):
        with open(self.path, "w", newline='') as f:
            f.write(self.data)


class RecordsTextDataFile(TextDataFile):
    @property
    def records(self):
        self.read_data()
        lines = self.data.splitlines()
        return len(lines)
