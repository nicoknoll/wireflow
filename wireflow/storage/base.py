class Storage:
    @classmethod
    def _init_instance(cls, instance_cls, state):
        instance = instance_cls.__new__(instance_cls)
        instance.__setstate__(state)
        return instance

    @classmethod
    def get_reverse_keys(cls, rel):
        raise NotImplementedError

    @classmethod
    def load(cls, key, instance_cls=None):
        raise NotImplementedError

    @classmethod
    def store(cls, key, value):
        raise NotImplementedError
