class cached_property(object):
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class classproperty(object):
    def __init__(self, method=None):
        self.func = method

    def __get__(self, instance, cls=None):
        return self.func(cls)

    def getter(self, method):
        self.func = method
        return self


class cached_classproperty:
    NOT_SET = object()

    def __init__(self, method):
        self.method = method
        self.cached_value = self.NOT_SET

    def __get__(self, instance, owner):
        if self.cached_value is not self.NOT_SET:
            return self.cached_value

        self.cached_value = self.method(owner)
        return self.cached_value

    def __set__(self, instance, value):
        self.cached_value = value

    def __delete__(self, instance):
        self.cached_value = self.NOT_SET
