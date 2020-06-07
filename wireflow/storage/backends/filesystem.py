import glob
import json
import os.path

from ..base import Storage
from ...util import cached_classproperty
from ... import config


class FileSystemStorage(Storage):
    @cached_classproperty
    def _directory(cls):
        return config.FILE_STORAGE_ROOT

    @classmethod
    def _file_get_contents(cls, filename):
        path = os.path.join(cls._directory, filename)
        with open(path, 'r') as f:
            return f.read()

    @classmethod
    def _file_write_contents(cls, filename, payload):
        path = os.path.join(cls._directory, filename)
        with open(path, 'w+') as f:
            return f.write(payload)

    @classmethod
    def _decode_filename(cls, encoded):
        return os.path.splitext(encoded.replace('__', ':'))[0]

    @classmethod
    def _encode_filename(cls, decoded):
        filename = decoded.replace(':', '__')
        return f'{filename}.json'

    @classmethod
    def _decode(cls, encoded):
        return json.loads(encoded)

    @classmethod
    def _encode(cls, decoded):
        return json.dumps(decoded)

    @classmethod
    def _init_instance(cls, instance_cls, state):
        instance = instance_cls.__new__(instance_cls)
        instance.__setstate__(state)
        return instance

    @classmethod
    def get_reverse_keys(cls, rel):
        return [
            cls._decode_filename(os.path.basename(f))
            for f in glob.glob(os.path.join(cls._directory, f'{rel}__*'))
        ]

    @classmethod
    def load(cls, key, instance_cls=None):
        filename = cls._encode_filename(key)
        data = cls._file_get_contents(filename)
        state = cls._decode(data)

        if instance_cls:
            return cls._init_instance(instance_cls, state)

        return state

    @classmethod
    def store(cls, key, value):
        filename = cls._encode_filename(key)
        cls._file_write_contents(filename, cls._encode(value))
