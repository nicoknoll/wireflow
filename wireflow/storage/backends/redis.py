try:
    import redis
except ImportError:
    raise ImportError('To use RedisStorage you need to install `redis`')

import json

from ..base import Storage


class RedisStorage(Storage):
    _storage = redis.Redis()

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
        return [k.decode('utf-8') for k in cls._storage.scan_iter(f'{rel}:*')]

    @classmethod
    def load(cls, key, instance_cls=None):
        key = key.decode('utf-8') if isinstance(key, bytes) else key
        state = cls._decode(cls._storage.get(key))

        if instance_cls:
            return cls._init_instance(instance_cls, state)

        return state

    @classmethod
    def store(cls, key, value):
        key = key.decode('utf-8') if isinstance(key, bytes) else key
        cls._storage.set(key, cls._encode(value))
