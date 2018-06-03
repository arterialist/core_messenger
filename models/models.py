class Category:
    def __init__(self, name, display_name):
        self.name = name
        self.display_name = display_name


class Setting:
    def __init__(self, key, value, setting_type, display_name):
        self.key = key
        self.value = value
        self.setting_type = setting_type
        self.display_name = display_name


class Settings:
    def __init__(self):
        self.__settings = dict()
        self.__new_settings = dict()

    def has(self, category: Category, setting: Setting):
        return setting in self.__settings.get(category, list())

    def set(self, category: Category, setting: Setting, init=False):
        if not self.has(category, setting):
            self.__settings[category] = list()
            if not init:
                self.__new_settings[category].append(setting)
        self.__settings[category].append(setting)

    def get(self, category, key):
        for setting in self.__settings.get(category, Category("", "")):
            if setting.key == key:
                return setting

    def is_new(self, category: Category, setting: Setting):
        return setting in self.__new_settings.get(category, list())

    def iterate(self):
        for category, settings in self.__settings.items():
            for setting in settings:
                yield category, setting


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
