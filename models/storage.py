class Settings:
    def __init__(self):
        self.__settings = dict()
        self.__new_keys = list()

    def has(self, key):
        return key in self.__settings

    def set(self, key, value, init=False):
        if not self.has(key) and not init:
            self.__new_keys.append(key)
        self.__settings[key] = value

    def get(self, key):
        self.__settings.get(key, "")

    def is_new(self, key):
        return key in self.__new_keys

    def iterate(self):
        for key, value in self.__settings.items():
            yield key, value


class Storage:
    def __init__(self):
        self.__storage = dict()
        self.__new_keys = list()

    def has(self, key):
        return key in self.__storage

    def set(self, key, value, init=False):
        if not self.has(key) and not init:
            self.__new_keys.append(key)
        self.__storage[key] = value

    def get(self, key):
        self.__storage.get(key, "")

    def is_new(self, key):
        return key in self.__new_keys

    def iterate(self):
        for key, value in self.__storage.items():
            yield key, value
