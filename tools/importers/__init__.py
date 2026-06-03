class BaseImporter:
    def __init__(self):
        self._warnings = []

    def warn(self, msg):
        self._warnings.append(msg)

    @property
    def warnings(self):
        return list(self._warnings)

    def load(self, filepath: str) -> list[dict]:
        raise NotImplementedError
