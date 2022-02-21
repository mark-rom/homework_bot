class APIErrException(Exception):
    """Custom Exception class for handling Practicum.Homeworks API errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
