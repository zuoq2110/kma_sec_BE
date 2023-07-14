
class InvalidArgumentException(Exception):

    def __init__(self, name: str):
        self.name = name


class ResourcesNotFoundException(Exception):

    def __init__(self, name: str):
        self.name = name
