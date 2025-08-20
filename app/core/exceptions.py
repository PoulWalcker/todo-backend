class DuplicateError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class CreationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
