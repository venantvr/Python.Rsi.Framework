from functools import wraps


class DoOnce:
    def __init__(self, func):
        self.func = func
        self.has_run = False

    def __call__(self, *args, **kwargs):
        if not self.has_run:
            self.has_run = True
            return self.func(*args, **kwargs)


def do_once_decorator(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_do_once_flag'):
            self._do_once_flag = {}
        if method.__name__ not in self._do_once_flag:
            self._do_once_flag[method.__name__] = True
            return method(self, *args, **kwargs)

    return wrapper
