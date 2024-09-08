import matplotlib


class MatplotlibBackendSwitcher:
    def __init__(self, new_backend):
        self.new_backend = new_backend
        self.original_backend = matplotlib.get_backend()

    def __enter__(self):
        matplotlib.use(self.new_backend)

    def __exit__(self, exc_type, exc_val, exc_tb):
        matplotlib.use(self.original_backend)
