class Storage:
    @classmethod
    def get_reverse_keys(cls, rel):
        raise NotImplementedError

    @classmethod
    def load(cls, key, instance_cls=None):
        raise NotImplementedError

    @classmethod
    def store(cls, key, value):
        raise NotImplementedError
