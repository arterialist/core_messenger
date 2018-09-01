class Category:
    def __init__(self, name, display_name):
        self.name = name
        self.display_name = display_name


class Categories:
    __categories = dict()

    @staticmethod
    def get_category(name: str, display_name: str) -> Category:
        if name not in Categories.__categories.keys():
            Categories.__categories[name] = Category(name, display_name)
        return Categories.__categories[name]


"""
setting type:
0 - checkbox
1 - editable
"""


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

    def set(self, possibly_new_category: Category, setting: Setting, init: bool = False):
        category = Categories.get_category(possibly_new_category.name, possibly_new_category.display_name)

        if init:
            if category not in self.__settings.keys():
                self.__settings[category] = list()

            self.__settings[category].append(setting)
            return

        if category not in self.__settings.keys():
            self.__settings[category] = list()
            self.__new_settings[category] = list()

        if setting not in self.__settings[category]:
            self.__settings[category].append(setting)

            if category not in self.__new_settings.keys():
                self.__new_settings[category] = list()

            if setting not in self.__new_settings[category]:
                self.__new_settings[category].append(setting)

        for existing_setting in self.__settings[category]:
            if existing_setting.key == setting.key:
                existing_setting.value = setting.value

        for existing_setting in self.__new_settings[category]:
            if existing_setting.key == setting.key:
                existing_setting.value = setting.value

    def get(self, category: Category, key: str) -> Setting:
        for setting in self.__settings.get(Categories.get_category(category.name, category.display_name), list()):
            if setting.key == key:
                return setting

    def is_new(self, possibly_new_category: Category, setting: Setting) -> bool:
        category = Categories.get_category(possibly_new_category.name, possibly_new_category.display_name)
        return setting in self.__new_settings.get(category, list())

    def is_new_category(self, possibly_new_category: Category) -> bool:
        category = Categories.get_category(possibly_new_category.name, possibly_new_category.display_name)
        return category in self.__new_settings

    def iterate(self) -> tuple:
        for category, settings in self.__settings.items():
            for setting in settings:
                yield category, setting

    def get_categories(self) -> list:
        return list(self.__settings.keys())

    def get_settings(self, category: Category) -> list:
        return self.__settings[category]


class Storage:
    def __init__(self):
        self.__storage = dict()
        self.__new_keys = list()

    def has(self, key: str) -> bool:
        return key in self.__storage

    def set(self, key: str, value: object, init: bool = False):
        if not self.has(key) and not init:
            self.__new_keys.append(key)
        self.__storage[key] = value

    def get(self, key: str) -> str:
        return self.__storage.get(key, "")

    def is_new(self, key: str) -> bool:
        return key in self.__new_keys

    def iterate(self) -> tuple:
        for key, value in self.__storage.items():
            yield key, value
