from ..base import Storage


CACHE = {}


class MemoryStorage(Storage):
    @classmethod
    def get_reverse_keys(cls, rel):
        return [k for k in CACHE.keys() if k.startswith(f'{rel}:')]

    @classmethod
    def load(cls, key, instance_cls=None):
        state = CACHE[key]  # fail ungracefully

        if instance_cls:
            return cls._init_instance(instance_cls, state)

        return state

    @classmethod
    def store(cls, key, value):
        CACHE[key] = value
