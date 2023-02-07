from pathlib import Path

from lxml import etree
from zeep import xsd, Settings

from .transport import Transport

XSD_PATH = Path('./request_sim_validity_consumer/soap/xsd')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Loader(metaclass=Singleton):
    def __init__(self, path=XSD_PATH):
        self._path = path
        self.schemas = dict()
        self.load()

    def load(self):
        for d in self.list_dirs(self._path):
            for f in self.list_files(d):
                tree = etree.parse(str(f))
                t = Transport(d)
                s = Settings(xsd_ignore_sequence_order=True)
                schema = xsd.Schema(tree.getroot(), transport=t, settings=s)
                self.schemas[str(f.name)[:-4]] = schema

    @staticmethod
    def list_dirs(path):
        return [x for x in path.iterdir() if x.is_dir()]

    @staticmethod
    def list_files(path):
        return [x for x in path.iterdir() if x.is_file()]

    def get_element(self, name_schema, name_element):
        template = '{{{}}}{}'
        for ns in self.schemas[name_schema].namespaces:
            fullname = template.format(ns, name_element)
            try:
                return self.schemas[name_schema].get_element(fullname)
            except:
                pass
