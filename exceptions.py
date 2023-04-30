class BackendError(Exception):
    """Will be raised if the backend cannot be imported in the hook process."""

    def __init__(self, traceback):
        self.traceback = traceback
