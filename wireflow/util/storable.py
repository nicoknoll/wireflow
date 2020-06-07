from wireflow import config

from .decorators import cached_classproperty
from .misc import import_string, generate_id


class Storable:
    prefix = None
    state_keys = ['id']

    @cached_classproperty
    def storage(cls):
        return import_string(config.STORAGE)

    def __init__(self):
        self.id = generate_id(self.prefix)

    def __getstate__(self):
        return {
            k: v for k, v in self.__dict__.items()
            if not self.state_keys or k in self.state_keys
        }

    def __setstate__(self, state):
        self.__dict__ = state

    def get_store_key(self):
        return self.id

    def store(self):
        return self.storage.store(self.get_store_key(), self.__getstate__())

    @classmethod
    def load(cls, key):
        return cls.storage.load(key, instance_cls=cls)


