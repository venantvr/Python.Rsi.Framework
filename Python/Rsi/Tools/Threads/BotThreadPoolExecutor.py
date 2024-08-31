import threading
from concurrent.futures import ThreadPoolExecutor


class BotThreadPoolExecutor:
    __instance = None
    __lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            with cls.__lock:
                if not cls.__instance:
                    cls.__instance = super(BotThreadPoolExecutor, cls).__new__(cls)
        return cls.__instance

    def __init__(self, max_workers=None):
        if not hasattr(self, 'executor'):
            self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, func, *args, **kwargs):
        return self.executor.submit(func, *args, **kwargs)

    def map(self, func, *iterables, timeout=None, chunksize=1):
        return self.executor.map(func, *iterables, timeout=timeout, chunksize=chunksize)

    def shutdown(self, wait=True):
        self.executor.shutdown(wait=wait)
