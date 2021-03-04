from collections.abc import MutableMapping


class Config(MutableMapping):
    def __init__(self):
        self._config = {}

    def __setitem__(self, key, value):
        self._config[key] = value

    def __getitem__(self, key):
        return self._config[key]

    def __delitem__(self, key):
        del self._config[key]

    def __len__(self):
        return self._config.__len__()

    def __iter__(self):
        yield self._config
