class Settings:
    def __init__(self):
        self.__settings = dict()
        self.__new_settings = dict()

    def has(self, category, key):
        return key in self.__settings[category]

    def set(self, category, key, value, init=False):
        if not self.has(category, key) and not init:
            self.__new_settings[category].append(key)
        self.__settings[category][key] = value

    def get(self, category, key):
        self.__settings.get(category, "").get(key, "")

    def is_new(self, category, key):
        return key in self.__new_settings[category]

    def iterate(self):
        for category, settings in self.__settings.items():
            for key, value in settings.items():
                yield category, key, value


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
